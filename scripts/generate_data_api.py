# generate_data_api.py
import aiohttp
import asyncio
import csv
import os
import time
from datetime import datetime
import pandas as pd
from statistics import mean

# === Configuration ===
API_URL = "http://192.168.1.173:8000/chat"  # ✅ endpoint non-stream
N_REQUESTS = 1000  # tu peux remettre 5000 une fois validé
CONCURRENCY = 20  # ajusté pour Mistral API gratuite
PROMPT = "j'ai un problème sur ma box elle clignote rouge"
MODELS = ["Mistral-medium", "Mistral-7B-Instruct"]

# === Répertoire Silver ===
SILVER_PATH = "../data/silver/"
os.makedirs(SILVER_PATH, exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
OUTPUT_CSV = os.path.join(SILVER_PATH, f"api_benchmark_{timestamp}.csv")


# ------------------------------------------------------
# 🧩 Envoi d'une requête asynchrone à l'API FastAPI locale
# ------------------------------------------------------
async def send_request(session, i):
    """Envoie une requête POST complète (non-stream) et récupère la réponse JSON."""
    model = MODELS[i % len(MODELS)]
    start_time = datetime.now()
    t0 = time.perf_counter()
    status_code = "ERROR"
    content = ""

    try:
        async with session.post(
            API_URL,
            json={"prompt": PROMPT, "model_selected": model},
            timeout=aiohttp.ClientTimeout(total=150)
        ) as response:
            status_code = response.status

            try:
                data = await response.json()
                content = data.get("response") or ""
            except Exception:
                # En cas de JSON invalide, lire le texte brut
                content = await response.text()

    except Exception as e:
        status_code = f"ERROR: {type(e).__name__}"
        content = f"Exception: {e}"

    duration = round(time.perf_counter() - t0, 3)
    end_time = datetime.now()

    return {
        "id": i,
        "model": model,
        "status_code": status_code,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_sec": duration,
        "response_text": str(content).strip()[:4000],
    }


# ------------------------------------------------------
# 🚀 Lancement parallèle du benchmark
# ------------------------------------------------------
async def run_benchmark():
    results = []
    connector = aiohttp.TCPConnector(limit_per_host=CONCURRENCY)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(1, N_REQUESTS + 1):
            tasks.append(send_request(session, i))

            # Exécution par lots
            if len(tasks) >= CONCURRENCY:
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
                tasks = []

                # Affichage progression
                print(f"{len(results)}/{N_REQUESTS} requêtes traitées...")

                # 🔹 Récapitulatif toutes les 20 requêtes
                if len(results) % 20 == 0:
                    print_intermediate_stats(results)

        # Dernier lot
        if tasks:
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

    return results


# ------------------------------------------------------
# 🔎 Récapitulatif intermédiaire
# ------------------------------------------------------
def print_intermediate_stats(results):
    """Affiche un résumé intermédiaire toutes les 20 requêtes."""
    df = pd.DataFrame(results)
    df["status_ok"] = df["status_code"].astype(str).str.startswith("200")

    for model in df["model"].unique():
        subset = df[df["model"] == model]
        success_rate = (subset["status_ok"].mean() * 100) if len(subset) > 0 else 0
        avg_duration = mean(subset["duration_sec"]) if len(subset) > 0 else 0
        print(f"   ↳ {model:<20} | taux succès: {success_rate:5.1f}% | durée moy: {avg_duration:5.3f}s")

    print("-" * 70)


# ------------------------------------------------------
# 💾 Sauvegarde CSV
# ------------------------------------------------------
def save_results_to_csv(results):
    """Sauvegarde les résultats dans un CSV sous data/silver."""
    if not results:
        print("Aucun résultat à enregistrer.")
        return

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Fichier généré : {OUTPUT_CSV}")
    print(f"📊 Nombre total de requêtes : {len(results)}")


# ------------------------------------------------------
# 📊 Analyse finale (taux de réussite + moyennes)
# ------------------------------------------------------
def analyze_results():
    df = pd.read_csv(OUTPUT_CSV)
    df["status_ok"] = df["status_code"].astype(str).str.startswith("200")
    df["duration_sec"] = pd.to_numeric(df["duration_sec"], errors="coerce")

    summary = (
        df.groupby("model")
        .agg(
            nb_requetes=("id", "count"),
            taux_reussite=("status_ok", "mean"),
            duree_moy=("duration_sec", "mean"),
            duree_med=("duration_sec", "median"),
            duree_max=("duration_sec", "max"),
        )
        .reset_index()
    )

    summary["taux_reussite"] = (summary["taux_reussite"] * 100).round(1).astype(str) + " %"
    summary["duree_moy"] = summary["duree_moy"].round(3)
    summary["duree_med"] = summary["duree_med"].round(3)
    summary["duree_max"] = summary["duree_max"].round(3)

    print("\n📈 Résumé final des performances par modèle :")
    print(summary.to_string(index=False))

    print("\n🧠 Analyse synthétique :")
    for _, row in summary.iterrows():
        if "local" in row["model"].lower() or "7b" in row["model"].lower():
            print(f"- {row['model']} → plus lent ({row['duree_moy']}s) mais stable ({row['taux_reussite']}).")
        else:
            print(f"- {row['model']} → plus rapide ({row['duree_moy']}s) mais dépend du quota API ({row['taux_reussite']}).")


# ------------------------------------------------------
# 🧠 Routine principale
# ------------------------------------------------------
async def main():
    print(f"🚀 Lancement de {N_REQUESTS} requêtes vers {API_URL}")
    start = time.perf_counter()

    results = await run_benchmark()
    save_results_to_csv(results)

    duration = round(time.perf_counter() - start, 2)
    print(f"\n⏱️ Durée totale du benchmark : {duration} sec")

    analyze_results()


if __name__ == "__main__":
    asyncio.run(main())
