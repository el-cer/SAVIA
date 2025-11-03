
import pandas as pd
import re, os
from datetime import datetime

RAW_PATH = "../data/raw/free tweet export 2.csv"
timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
print(f"{timestamp}")
SILVER_PATH = f"../data/silver/tweets_cleane_2.csv"
QUALITY_LOG_PATH  = "../quality/quality_log_tweets.csv"



def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"@[\w_]+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"["
                  u"\U0001F600-\U0001F64F"
                  u"\U0001F300-\U0001F5FF"
                  u"\U0001F680-\U0001F6FF"
                  u"\U0001F1E0-\U0001F1FF"
                  "]+", "", text, flags=re.UNICODE)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

df = pd.read_csv(RAW_PATH)
# 🧼 Application du nettoyage
df["clean_text"] = df["full_text"].apply(clean_text)
df["cleaned_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
     
# 🚫 Suppression des comptes officiels (Free, Iliad, Assistance, etc.)
EXCLUDED_ACCOUNTS = [
    "free", "free_1337", "free1337", "groupeiliad", "iliad",
    "free_officiel", "free_official", "groupe_iliad",
    "assistance freebox", "assistance_freebox"
]

# Normalisation des noms en minuscules sans accents (optionnel)
import unicodedata

def normalize_text(s):
    if pd.isna(s):
        return ""
    s = str(s).lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
def text_length(s):
    if pd.isna(s):
        return 0
    return len(s)
df["screen_name_clean"] = df["screen_name"].apply(normalize_text)
df["name_clean"] = df["name"].apply(normalize_text)
df["text_length"] = df["clean_text"].apply(text_length)

# Filtrage
df_clean = df[
    ~df["screen_name_clean"].isin(EXCLUDED_ACCOUNTS) &
    ~df["name_clean"].isin(EXCLUDED_ACCOUNTS)&
    df["in_reply_to"].isna()
].copy()

print(f"✅ {len(df) - len(df_clean)} comptes officiels exclus.")
df_clean[["screen_name", "name"]].drop_duplicates().head()
df_clean = df_clean[df_clean["text_length"] > 0]

os.makedirs(os.path.dirname(SILVER_PATH), exist_ok=True)
df_clean[["id", "created_at", "screen_name", "full_text", "clean_text", "cleaned_at"]].to_csv(SILVER_PATH, index=False)
print(f"✅ Exporté vers : {SILVER_PATH}")
    