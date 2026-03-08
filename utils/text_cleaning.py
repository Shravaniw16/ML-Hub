import pandas as pd
import re


# =============================
# TEXT CLEANING FUNCTION
# =============================
def clean_text(text):

    text = str(text).lower()

    # remove urls
    text = re.sub(r"http\S+", "", text)

    # remove punctuation & numbers
    text = re.sub(r"[^a-z\s]", "", text)

    # remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# =============================
# MAIN PROCESS FUNCTION
# =============================
def process_text_file(filepath):

    df = pd.read_csv(filepath)

    # -----------------------------
    # NORMALIZE COLUMN NAMES
    # -----------------------------
    df.columns = df.columns.str.strip().str.lower()

    # -----------------------------
    # FIND TEXT COLUMN AUTOMATICALLY
    # -----------------------------
    possible_text_cols = ["text", "review", "comment", "sentence"]

    text_col = None

    for col in possible_text_cols:
        if col in df.columns:
            text_col = col
            break

    if text_col is None:
        raise ValueError(
            "Dataset must contain a text column like 'text', 'review', 'comment', or 'sentence'"
        )

    # -----------------------------
    # FIND SENTIMENT COLUMN (OPTIONAL)
    # -----------------------------
    sentiment_col = None

    for col in ["sentiment", "label", "class"]:
        if col in df.columns:
            sentiment_col = col
            break

    # -----------------------------
    # REMOVE MISSING TEXT
    # -----------------------------
    df = df.dropna(subset=[text_col])

    # Remove empty rows
    df = df[df[text_col].astype(str).str.strip() != ""]

    # -----------------------------
    # REMOVE DUPLICATES
    # -----------------------------
    df = df.drop_duplicates()

    # -----------------------------
    # STORE ORIGINAL TEXT
    # -----------------------------
    df["original_text"] = df[text_col]

    # -----------------------------
    # CLEAN TEXT
    # -----------------------------
    df["cleaned_text"] = df["original_text"].apply(clean_text)

    # Remove rows that become empty after cleaning
    df = df[df["cleaned_text"].str.strip() != ""]

    # -----------------------------
    # TEXT STATISTICS
    # -----------------------------
    df["word_count"] = df["cleaned_text"].apply(lambda x: len(x.split()))

    df["char_count"] = df["cleaned_text"].apply(len)

    # -----------------------------
    # SENTIMENT → LABEL
    # -----------------------------
    if sentiment_col:

        label_map = {
            "positive": 1,
            "negative": 0
        }

        df["label"] = (
            df[sentiment_col]
            .astype(str)
            .str.lower()
            .map(label_map)
        )

        # remove rows where label not mapped
        df = df.dropna(subset=["label"])

        df["label"] = df["label"].astype(int)

    else:
        df["label"] = None

    # -----------------------------
    # FINAL DATASET
    # -----------------------------
    clean_df = df[
        [
            "original_text",
            "cleaned_text",
            "word_count",
            "char_count",
            "label"
        ]
    ]

    return clean_df