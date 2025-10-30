import requests
import json

# === CONFIGURATION ===
API_URL = "https://saviapi.win/classify"

MODEL = "Mistral-7B-Instruct"
tweet = "Je n'ai plus de connexion Internet depuis ce matin, ma box clignote rouge. #freemerde"

payload = {
        "prompt": tweet,
        "model": MODEL,
        "context": ""
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
