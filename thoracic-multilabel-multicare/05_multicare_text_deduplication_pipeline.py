import pandas as pd
from pathlib import Path

# ==== CONFIGURATION ====
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_CSV = BASE_DIR / "data" / "xray_thorax_filtered" / "merged_all.csv"
OUTPUT_CSV = BASE_DIR / "data" / "xray_thorax_filtered" / "merged_all_cleaned.csv"

# Column containing text data
text_column = "case_text"  # update if needed

# ==== STEP 1: Load CSV ====
df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

print(f"Original total rows: {len(df)}")
print(f"Unique 'file' names before cleaning: {df['file'].nunique()}")

# ==== STEP 2: Merge texts per (file, patient_id) ====
merged_texts = (
    df.groupby(['file', 'patient_id'])[text_column]
      .apply(lambda x: ' '.join(t for t in x if t.strip()))
      .reset_index()
)

# ==== STEP 3: Keep metadata + attach merged text ====
df_unique_meta = df.drop_duplicates(subset=['file', 'patient_id'], keep='first')

df_merged = pd.merge(
    df_unique_meta.drop(columns=[text_column]),
    merged_texts,
    on=['file', 'patient_id'],
    how='left'
)

# ==== STEP 4: Ensure one row per file ====
df_final = df_merged.drop_duplicates(subset=['file'], keep='first')

print(f"Final rows after cleaning: {len(df_final)}")
print(f"Unique 'file' names after cleaning: {df_final['file'].nunique()}")

# ==== STEP 5: Save result ====
df_final.to_csv(OUTPUT_CSV, index=False)

print(f"Cleaned dataset saved to: {OUTPUT_CSV}")