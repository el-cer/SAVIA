import requests

API_URL = "http://192.168.1.173:8000/chat"
PROMPT = "j'ai un problème sur ma box elle clignote rouge"
MODELS = ["Mistral-medium", "Mistral-7B-Instruct"]

for model in MODELS:
    print(f"\n=== Test du modèle : {model} ===")
    payload = {
        "prompt": PROMPT,
        "model_selected": model
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        print(f"Status code : {response.status_code}")
        print("Contenu brut :", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion : {e}")
