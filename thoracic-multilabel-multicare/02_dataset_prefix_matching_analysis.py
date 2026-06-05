import pandas as pd
from pathlib import Path

# === Dataset directory  ===
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# === Load files ===
captions = pd.read_csv(DATA_DIR / "captions_and_labels.csv")
case_images = pd.read_parquet(DATA_DIR / "case_images.parquet")

# === Extract prefix before underscore in both datasets ===
captions['article_prefix'] = (
    captions['main_image']
    .astype(str)
    .str.split('_')
    .str[0]
    .str.lower()
)

case_images['article_prefix'] = (
    case_images['article_id']
    .astype(str)
    .str.split('_')
    .str[0]
    .str.lower()
)

# === Count unique prefixes in each ===
print(f"Unique article prefixes in captions: {captions['article_prefix'].nunique()}")
print(f"Unique article prefixes in case_images: {case_images['article_prefix'].nunique()}")

# === Find intersection of prefixes ===
common_prefixes = set(captions['article_prefix']) & set(case_images['article_prefix'])
print(f"Common prefixes count: {len(common_prefixes)}")

# === Preview some matching prefixes ===
print("\nSample common prefixes:", list(common_prefixes)[:10])

# === Check sample rows with a common prefix ===
if common_prefixes:
    sample_prefix = list(common_prefixes)[:1]

    print("\nSample rows from captions with this prefix:")
    print(captions[captions['article_prefix'].isin(sample_prefix)].head())

    print("\nSample rows from case_images with this prefix:")
    print(case_images[case_images['article_prefix'].isin(sample_prefix)].head())