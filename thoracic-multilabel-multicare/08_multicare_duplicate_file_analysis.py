import pandas as pd
from pathlib import Path

# === Paths  ===
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_CSV = BASE_DIR / "data" / "xray_thorax_filtered" / "merged_all.csv"
OUTPUT_CSV = BASE_DIR / "data" / "xray_thorax_filtered" / "duplicate_files_exact.csv"

# === Read CSV ===
df = pd.read_csv(INPUT_CSV, dtype=str)

# === Filter non-empty file entries ===
non_empty = df[df['file'].notna() & (df['file'].str.strip() != "")]

# === Count duplicates ===
duplicate_rows_count = non_empty['file'].duplicated().sum()

print(f"Total rows in CSV: {len(df)}")
print(f"Rows with non-empty 'file': {len(non_empty)}")
print(f"Exact duplicate file entries: {duplicate_rows_count}")

# === Extract all duplicate rows ===
duplicates_df = non_empty[non_empty['file'].duplicated(keep=False)]

# === Save output ===
duplicates_df.to_csv(OUTPUT_CSV, index=False)

print(f"Exact duplicates saved to: {OUTPUT_CSV}")