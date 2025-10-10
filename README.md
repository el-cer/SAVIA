# SAVIA — Solution Digitale SAV via Tweets + LLM + Chatbot

SAVIA est une solution modulaire de support client (SAV) qui :

- Capte des tweets mentionnant un opérateur télécom
- Classe automatiquement les messages en **plainte avérée ou non**
- Redirige les clients vers un **agent conversationnel LLM**
- Permet un traitement autonome ou un transfert vers un humain

---

##  Architecture

- `data/` : tweets CSV, nettoyage, classification ML
- `backend/` : API Flask/FastAPI qui détecte les plaintes et appelle le LLM
- `frontend/` : interface utilisateur (Next.js)
- `docker/` : conteneurisation front + back

---

##  Lancement local

```bash
git clone git@github.com:el-cer/SAVIA.git
cd SAVIA
docker-compose up --build
