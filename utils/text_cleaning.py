import pandas as pd
import re

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)      # remove URLs
    text = re.sub(r"[^a-z\s]", "", text)     # remove punctuation & numbers
    text = re.sub(r"\s+", " ", text).strip()
    return text


def process_text_file(filepath):
    df = pd.read_csv(filepath)

    # -----------------------------
    # REQUIRED COLUMNS CHECK
    # -----------------------------
    if "text" not in df.columns or "sentiment" not in df.columns:
        raise ValueError("Dataset must contain 'text' and 'sentiment' columns")

    # -----------------------------
    # DROP DUPLICATES & NULLS
    # -----------------------------
    df = df.drop_duplicates()
    df = df.dropna(subset=["text", "sentiment"])

    # -----------------------------
    # CLEAN TEXT
    # -----------------------------
    df["cleaned_text"] = df["text"].apply(clean_text)

    # -----------------------------
    # SENTIMENT → LABEL (CRITICAL FIX)
    # -----------------------------
    label_map = {
        "positive": 1,
        "negative": 0
    }

    df["label"] = (
        df["sentiment"]
        .astype(str)
        .str.lower()
        .map(label_map)
    )

    # Remove rows like "neutral"
    df = df.dropna(subset=["label"])

    # Convert to int
    df["label"] = df["label"].astype(int)
    print("DEBUG LABEL VALUES:", df["label"].unique())


    # -----------------------------
    # FINAL CLEAN DATASET
    # -----------------------------
    clean_df = df[["cleaned_text", "label"]]

    return clean_df
