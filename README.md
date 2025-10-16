# SAVIA — Solution Digitale SAV via Tweets + LLM + Chatbot

**SAVIA** est une solution modulaire de support client (SAV) qui repose sur l’analyse de tweets, un pipeline de classification, et un chatbot basé sur un LLM local ou distant.  
L’objectif est d’améliorer la qualité du service client en automatisant la détection, la compréhension et la réponse aux messages clients.

---

## 🚀 Fonctionnalités

- 📡 Ingestion de tweets ou messages utilisateurs
- 🤖 Classification des messages (plainte, remerciement, etc.)
- 💬 Chatbot intelligent via LLM local (llama.cpp) ou cloud (OpenAI/Mistral API)
- 📊 Monitoring complet avec Grafana (qualité du modèle, temps de réponse, qualité des données)
- 🛠️ Stack conteneurisée (Next.js, FastAPI, PostgreSQL, Prometheus, Grafana)

---

## 🧱 Architecture technique

![Architecture SAVIA](./images/Architecture_diagramm.png)

### 🔹 Frontend (repo courant : `SAVIA`)

- Interface utilisateur Next.js (hébergée sur Cloudflare Pages)
- Envoie les messages vers le backend via `/chat_sav`
- Intègre les dashboards Grafana via iframe

### 🔹 Backend (repo distinct : [`SAVIA-API-LLM`](https://github.com/el-cer/SAVIA-API-LLM))

- FastAPI BFF exposant les endpoints :
  - `/classify` → classification des messages
  - `/chat_sav` → génération de réponse via LLM
  - `/metrics` → métriques Prometheus
- Connecté à :
  - un modèle local (`llama.cpp`)
  - ou un modèle distant (`Mistral API`, `OpenAI`)

### 🔹 Database

- PostgreSQL avec TimescaleDB pour stocker :
  - les conversations
  - les feedbacks utilisateurs
  - les métriques LLM

### 🔹 Monitoring (via Grafana)

- Prometheus scrape les métriques des appels LLM
- Dashboards intégrés :
  - Qualité du modèle de classification
  - Qualité du chatbot (latence, résolution)
  - Qualité de la donnée entrante (nulls, texte vide, etc.)

---

## 🧪 Lancement local

```bash
git clone git@github.com:el-cer/SAVIA.git
cd SAVIA
docker-compose up --build

