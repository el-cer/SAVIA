import requests
import os
import pandas as pd
from datetime import datetime
import time
from tqdm import tqdm

API_URL = "https://saviapi.win/classify"
INPUT_CSV = "../data/silver/tweets_cleaned_1.csv"
OUTPUT_CSV = "../data/gold/tweets_classified_2_test_tété.csv"
MODEL = "Mistral-7B-Instruct"

CLASSIFICATION_CONTEXT = (
    "Tu es un assistant expert du Service Après-Vente (SAV) de l’opérateur Free. "
    "Ton objectif est d'analyser un tweet client et de déterminer s’il décrit un problème technique réel ou non, "
    "puis de classer ce problème par domaine et sous-domaine.\n\n"

    "⚠️ Ne considère pas comme 'problème avéré' les tweets humoristiques, ironiques, publicitaires, "
    "ou ceux qui ne contiennent aucun signe de plainte réelle ou technique.\n\n"

    "🔸 Le résultat doit toujours être un JSON unique au format :\n"
    "{\"label\": label, \"domaine\": domaine, \"sous_domaine\": sous_domaine, \"score\": score}\n\n"

    "🔹 'score' = niveau de confiance entre 0.0 et 1.0.\n\n"

    "🔹 Choix possibles :\n"
    "- label : ['problème avéré', 'problème non avéré']\n"
    "- domaine : ['mobile', 'fixe', 'facture', 'contact']\n"
    "- sous_domaine : ['réseau', 'wifi', 'box', 'appel voix', 'sécurité', 'autres']\n\n"

    "🧭 Guide de décision :\n"
    "- Si le tweet demande un **conseiller, une aide, ou mentionne une panne/dysfonctionnement**, choisis 'problème avéré'.\n"
    "- Si le message est **vague, court, ironique ou sans signe de problème**, choisis 'problème non avéré'.\n"
    "- Si le texte parle de **connexion Internet, lenteur, perte de signal**, choisis domaine='fixe', sous_domaine='réseau' ou 'wifi'.\n"
    "- Si le texte parle de **carte SIM, 4G, 5G, appels, SMS**, choisis domaine='mobile', sous_domaine='appel voix' ou 'réseau'.\n"
    "- Si le texte évoque **facture, prélèvement, paiement, compte client**, choisis domaine='facture'.\n"
    "- Si le texte mentionne **mot de passe, piratage, sécurité**, choisis sous_domaine='sécurité'.\n"
    "- Si le tweet est un **mème, une blague, ou hors sujet technique**, choisis toujours 'problème non avéré'.\n"
    "- Si un tweet exprime une similarité avec un autre (par exemple “idem”, “pareil pour moi”, “moi aussi”), on privilégie alors la catégorie 'problème avéré'.\n"

    "🧠 Analyse le texte avec bon sens. Ne crée jamais de nouvelles catégories. "
    "Sois sobre, rigoureux et évite toute surclassification."
)
json_results = []
timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
print(f"{timestamp} - Début de la classification des tweets avec le modèle {MODEL}")


df = pd.read_csv(INPUT_CSV)

json_results = []
print(df.head())
print(f"🧠 Début de la classification ({len(df)} tweets) - modèle {MODEL}")

def classify_text(row, retries=3):
    tweet = str(row["clean_text"])
    payload = {"prompt": tweet, "model": MODEL, "context": CLASSIFICATION_CONTEXT}
    start = time.perf_counter()
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": row["id"],
                    "label": data.get("label", "Unknown"),
                    "domaine": data.get("domaine", "Unknown"),
                    "sous_domaine": data.get("sous_domaine", "Unknown"),
                    "score": data.get("score", None),
                    "status_code": response.status_code,
                    "duration_seconds": round(time.perf_counter() - start, 3)
                }
            else:
                print(f"⚠️ Erreur API : {response.status_code}, tentative {attempt+1}/3")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ {e} (tentative {attempt+1}/3)")
            time.sleep(2)
    return {"id": row["id"], "label": "Error", "status_code": "ERROR"}

# === BOUCLE PRINCIPALE ===
for _, row in tqdm(df.iterrows(), total=len(df), desc="🔍 Classification"):
    json_results.append(classify_text(row))

df_out = pd.merge(df, pd.DataFrame(json_results), on="id", how="left")
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
df_out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"✅ Export terminé vers : {OUTPUT_CSV}")