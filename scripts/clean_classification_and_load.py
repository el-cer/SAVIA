# clean_classification_and_load.py
import os
import re
import unicodedata
import pandas as pd
from datetime import datetime

# --- IO ---
INPUT_CSV  = "../data/gold/tweets_classified_2_final.csv"     # ton fichier actuel
OUTPUT_CSV = "../data/gold/tweets_classified_clean_final_théthé.csv"

# --- Vocabulaire canonique ---
LABELS_CANON = ["problème avéré", "problème non avéré", "inconnu"]
DOMAINES_CANON = ["mobile", "fixe", "facture", "aucun", "inconnu"]
SOUSDOMS_CANON = ["réseau", "wifi", "box", "appel voix", "sécurité", "aucun", "inconnu"]

# --- Synonymes / corrections fréquentes ---
MAP_LABEL = {
    "probleme avere": "problème avéré",
    "probleme non avere": "problème non avéré",
    "problème avere": "problème avéré",
    "problème non avere": "problème non avéré",
    "ok": "problème non avéré",
    "aucun": "problème non avéré",
}

MAP_DOMAINE = {
    "internet": "fixe",
    "box": "fixe",
    "fixes": "fixe",
    "factures": "facture",
    "mobile ou fixe": "inconnu",
    "aucun": "aucun",
    "none": "aucun",
}

MAP_SOUSDOM = {
    "reseau": "réseau",
    "wifi ": "wifi",
    "wifi/internet": "wifi",
    "internet": "réseau",
    "appel": "appel voix",
    "voix": "appel voix",
    "securite": "sécurité",
    "boxe": "box",
    "aucun": "aucun",
    "none": "aucun",
}

def strip_accents(s: str) -> str:
    s = str(s or "").strip().lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = re.sub(r"\s+", " ", s)
    return s

def pick_first_token(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s).strip()
    if s.startswith('["') or s.startswith("['"):
        s = s.strip("[]'\"")
    if "/" in s:
        s = s.split("/")[0].strip()
    if "," in s:
        s = s.split(",")[0].strip()
    return s

def normalize_label(x: str) -> str:
    raw = strip_accents(x)
    raw = MAP_LABEL.get(raw, raw)
    return raw if raw in LABELS_CANON else "inconnu"

def normalize_domaine(x: str) -> str:
    raw = strip_accents(pick_first_token(x))
    raw = MAP_DOMAINE.get(raw, raw)
    return raw if raw in DOMAINES_CANON else "inconnu"

def normalize_sousdom(x: str) -> str:
    raw = strip_accents(pick_first_token(x))
    raw = MAP_SOUSDOM.get(raw, raw)
    return raw if raw in SOUSDOMS_CANON else "inconnu"

def enforce_rules(row):
    if row["label"] == "problème non avéré":
        row["domaine"] = "aucun"
        row["sous_domaine"] = "aucun"
    return row

def quality_flags(row):
    flags = []
    if row["label"] not in LABELS_CANON:
        flags.append("label_oov")
    if row["domaine"] not in DOMAINES_CANON:
        flags.append("domaine_oov")
    if row["sous_domaine"] not in SOUSDOMS_CANON:
        flags.append("sous_domaine_oov")
    return ",".join(flags) if flags else ""

def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.read_csv(INPUT_CSV)

    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"])

    df["label"] = df.get("label", "inconnu").apply(normalize_label)
    df["domaine"] = df.get("domaine", "inconnu").apply(normalize_domaine)
    df["sous_domaine"] = df.get("sous_domaine", "inconnu").apply(normalize_sousdom)

    df = df.apply(enforce_rules, axis=1)

    df["quality_flags"] = df.apply(quality_flags, axis=1)
    df["cleaned_at"] = ts

    cols_first = [
        "id", "created_at", "screen_name", "full_text", "clean_text",
        "label", "domaine", "sous_domaine",
        "model", "status_code", "request_time", "duration_seconds",
        "quality_flags", "cleaned_at"
    ]
    cols = [c for c in cols_first if c in df.columns] + [c for c in df.columns if c not in cols_first]
    df = df[cols]

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Export Gold propre : {OUTPUT_CSV}")

if __name__ == "__main__":
    main()