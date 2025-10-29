import requests
import os
import pandas as pd
from datetime import datetime
import time

API_URL = "https://saviapi.win/classify"
INPUT_CSV = "../data/silver/tweets_cleaned_1.csv"
OUTPUT_CSV = "../data/gold/tweets_classified_1.csv"
MODEL = "Mistral-7B-Instruct"

json_results = []
timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
print(f"{timestamp} - Début de la classification des tweets avec le modèle {MODEL}")

df = pd.read_csv(INPUT_CSV)

def classify_text(row):
    """Appelle l’API /classify et renvoie un dictionnaire avec les résultats"""
    time.sleep(0.5)  # éviter surcharge
    start_time = time.perf_counter()
    start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tweet = row["clean_text"]
    payload = {
        "prompt": tweet,
        "model": MODEL,
        "context": ""
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        duration = round(time.perf_counter() - start_time, 3)

        if response.status_code == 200:
            data = response.json()
            result = {
                "id": row["id"],
                "prompt": tweet,
                "label": data.get("label", "Unknown"),
                "domaine": data.get("domaine", "Unknown"),
                "sous_domaine": data.get("sous_domaine", "Unknown"),
                "model": MODEL,
                "status_code": response.status_code,
                "request_time": start_datetime,
                "duration_seconds": duration
            }
        else:
            result = {
                "id": row["id"],
                "prompt": tweet,
                "label": "Error",
                "domaine": "Error",
                "sous_domaine": "Error",
                "model": MODEL,
                "status_code": response.status_code,
                "request_time": start_datetime,
                "duration_seconds": duration
            }

        return result

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur réseau : {e}")
        return {
            "id": row["id"],
            "prompt": tweet,
            "label": "Exception",
            "domaine": "Exception",
            "sous_domaine": "Exception",
            "model": MODEL,
            "status_code": "ERROR",
            "request_time": start_datetime,
            "duration_seconds": 0
        }

for index, row in df.iterrows():
    print(f"\n🧠 Classifying tweet {index + 1}/{len(df)} (ID: {row['id']})")
    print(f"→ {row['clean_text']}")
    classification_result = classify_text(row)
    json_results.append(classification_result)

df_results = pd.DataFrame(json_results)
df_final = pd.merge(df, df_results, on="id", how="left")

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
df_final.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"\n✅ Fichier exporté vers : {OUTPUT_CSV}")
