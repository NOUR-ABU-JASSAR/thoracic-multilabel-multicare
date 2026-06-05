import pandas as pd
from pathlib import Path

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "xray_thorax_filtered"
OUTPUT_PATH = DATA_DIR / "merged_all.csv"

# === Load filtered files ===
captions = pd.read_csv(DATA_DIR / "captions_filtered.csv")
case_images = pd.read_parquet(DATA_DIR / "case_images_filtered.parquet")
cases = pd.read_parquet(DATA_DIR / "cases_filtered.parquet")
metadata = pd.read_parquet(DATA_DIR / "metadata_filtered.parquet")
abstracts = pd.read_parquet(DATA_DIR / "abstracts_filtered.parquet")

# === Merge step-by-step ===
merged = captions.merge(
    case_images,
    left_on="main_image_id",
    right_on="norm_case_id",
    how="inner",
    suffixes=("_capt", "_img")
)

merged = merged.merge(
    cases,
    on="case_id",
    how="inner",
    suffixes=("", "_case")
)

merged = merged.merge(
    metadata,
    on="article_id",
    how="left",
    suffixes=("", "_meta")
)

merged = merged.merge(
    abstracts,
    on="article_id",
    how="left",
    suffixes=("", "_abs")
)

# === Save output ===
merged.to_csv(OUTPUT_PATH, index=False)

print(f"Merged file saved at: {OUTPUT_PATH}")
print(f"Total rows in merged file: {len(merged)}")