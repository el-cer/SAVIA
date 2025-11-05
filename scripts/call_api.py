import requests
import json
import pandas as pd
import os
# === CONFIGURATION ===
API_URL = "https://saviapi.win/classify"

MODEL = "Mistral-7B-Instruct"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(PROJECT_ROOT)
# Construction du chemin relatif
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "silver", "tweets_cleaned_1.csv")

df = pd.read_csv(CSV_PATH)
tweet = df[df["id"]==1814368963826164172]["clean_text"].values[0]

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
    "- Si le tweet est un **mème, une blague, ou hors sujet technique**, choisis toujours 'problème non avéré'.\n\n"
    "- Si un tweet exprime une similarité avec un autre (par exemple “idem”, “pareil pour moi”, “moi aussi”), on privilégie alors la catégorie 'problème avéré'.\n"

    "🧠 Analyse le texte avec bon sens. Ne crée jamais de nouvelles catégories. "
    "Sois sobre, rigoureux et évite toute surclassification."
)

payload = {
        "prompt": tweet,
        "model": MODEL,
        "context": CLASSIFICATION_CONTEXT
    }

print(f"🔍 Envoi du texte à classifier vers {API_URL}...")
print(f"🧾 Contenu : {tweet}\n")

try:
    response = requests.post(API_URL, json=payload, timeout=60)

    print(f"✅ Status code : {response.status_code}")
    print("📦 Réponse brute :")
    print(response.text)

    # Si la réponse est au format JSON
    try:
        data = response.json()
        print("\n🔍 JSON parsé :")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print("\n⚠️ Impossible de parser la réponse en JSON")

except requests.exceptions.RequestException as e:
    print(f"❌ Erreur de connexion : {e}")
