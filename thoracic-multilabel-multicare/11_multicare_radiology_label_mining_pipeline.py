import os
import re
import pandas as pd
from collections import Counter, defaultdict
from pathlib import Path

# =========================================================
# CONFIGURATION 
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_CSV = BASE_DIR / "data" / "xray_thorax_filtered" / "merged_all_cleaned.csv"
TEXT_COL = "case_text"
OUTPUT_SUFFIX = "_scanned"

MIN_UNIGRAM_COUNT = 10
MIN_BIGRAM_COUNT = 8
MIN_TRIGRAM_COUNT = 5

TOP_K_UNIGRAMS = 300
TOP_K_BIGRAMS = 300
TOP_K_TRIGRAMS = 300

COMPUTE_COOCCURRENCE = True


# =========================================================
# SEED LABEL DICTIONARY
# =========================================================
SEED_LABELS = {
    "pneumonia": ["pneumonia", "bronchopneumonia", "lobar pneumonia"],
    "pleural_effusion": ["pleural effusion", "pleural fluid"],
    "atelectasis": ["atelectasis", "lung collapse"],
    "pneumothorax": ["pneumothorax", "collapsed lung"],
    "cardiomegaly": ["cardiomegaly", "enlarged heart"],
    "pulmonary_edema": ["pulmonary edema", "lung edema"],
    "lung_mass_or_cancer": [
        "lung cancer", "pulmonary carcinoma", "lung mass", "bronchogenic carcinoma"
    ],
    "interstitial_lung_disease": [
        "interstitial lung disease", "ild", "pulmonary fibrosis"
    ],
    "bronchitis": ["bronchitis"],
    "emphysema": ["emphysema"],
    "tuberculosis": ["tuberculosis", "tb"],
    "covid19": ["covid-19", "covid19", "sars-cov-2"],
    "infection": ["infection", "sepsis"],
    "congestive_heart_failure": ["congestive heart failure", "chf"],
    "heart_failure": ["heart failure"],
    "stroke": ["stroke", "cva"],
}


# =========================================================
# TEXT NORMALIZATION
# =========================================================
def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\-\s/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =========================================================
# LABEL SCANNING
# =========================================================
def scan_labels(df, text_col, seed_labels):
    for label in seed_labels:
        df[label] = 0

    for idx, text in df[text_col].fillna("").items():
        txt = normalize_text(text)

        for label, terms in seed_labels.items():
            for t in terms:
                if re.search(r"\b" + re.escape(t.lower()) + r"\b", txt):
                    df.at[idx, label] = 1
                    break

    return df


# =========================================================
# N-GRAM MINING
# =========================================================
def tokenize(text):
    text = normalize_text(text).replace("/", " ")
    return [t for t in text.split() if t]


def ngrams(tokens, n):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def scan_ngrams(df, text_col, seed_labels):
    dict_terms = set()
    for terms in seed_labels.values():
        for t in terms:
            dict_terms.add(t.lower())

    uni = Counter()
    bi = Counter()
    tri = Counter()

    for text in df[text_col].fillna(""):
        toks = tokenize(text)
        uni.update(toks)
        bi.update([b for b in ngrams(toks, 2) if b not in dict_terms])
        tri.update([t for t in ngrams(toks, 3) if t not in dict_terms])

    uni_df = pd.DataFrame(uni.items(), columns=["term", "count"])
    bi_df = pd.DataFrame(bi.items(), columns=["term", "count"])
    tri_df = pd.DataFrame(tri.items(), columns=["term", "count"])

    return uni_df, bi_df, tri_df


# =========================================================
# COOCCURRENCE MATRIX
# =========================================================
def cooccurrence_matrix(df, labels):
    pairs = defaultdict(int)
    totals = Counter()

    for _, row in df.iterrows():
        active = [l for l in labels if row[l] == 1]
        for i in range(len(active)):
            totals[active[i]] += 1
            for j in range(i + 1, len(active)):
                key = tuple(sorted((active[i], active[j])))
                pairs[key] += 1

    mat = pd.DataFrame(0, index=labels, columns=labels)

    for (a, b), v in pairs.items():
        mat.at[a, b] = v
        mat.at[b, a] = v

    for l in labels:
        mat.at[l, l] = totals[l]

    return mat


# =========================================================
# MAIN PIPELINE
# =========================================================
def main():
    df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

    if TEXT_COL not in df.columns:
        raise ValueError(f"Missing column: {TEXT_COL}")

    # Label scanning
    labeled_df = scan_labels(df.copy(), TEXT_COL, SEED_LABELS)

    # N-gram mining
    uni_df, bi_df, tri_df = scan_ngrams(df, TEXT_COL, SEED_LABELS)

    # Output paths
    out_prefix = str(INPUT_CSV).replace(".csv", "") + OUTPUT_SUFFIX

    labeled_df.to_csv(out_prefix + "_labels.csv", index=False)
    uni_df.to_csv(out_prefix + "_unigrams.csv", index=False)
    bi_df.to_csv(out_prefix + "_bigrams.csv", index=False)
    tri_df.to_csv(out_prefix + "_trigrams.csv", index=False)

    print("Saved labeled dataset and n-gram outputs")

    # Co-occurrence
    if COMPUTE_COOCCURRENCE:
        mat = cooccurrence_matrix(labeled_df, list(SEED_LABELS.keys()))
        mat.to_csv(out_prefix + "_cooccurrence.csv")
        print("Saved co-occurrence matrix")


if __name__ == "__main__":
    main()