import pandas as pd
from pathlib import Path

# ==== CONFIGURATION ====
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_CSV = BASE_DIR / "data" / "xray_thorax_filtered" / "merged_all.csv"
OUTPUT_CSV = BASE_DIR / "data" / "xray_thorax_filtered" / "merged_all_cleaned.csv"

text_column = "case_text"  # adjust if needed

# ==== STEP 1: Load CSV ====
df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

print(f"Original total rows: {len(df)}")
print(f"Unique 'file' names before cleaning: {df['file'].nunique()}")

# ==== STEP 2: Merge texts per (file, patient_id) ====
df_merged = (
    df.groupby(['file', 'patient_id'], as_index=False)
      .agg({text_column: ' '.join})
)

print(f"Rows after merging by file & patient_id: {len(df_merged)}")

# ==== STEP 3: Ensure one row per file ====
df_final = df_merged.drop_duplicates(subset=['file'], keep='first')

print(f"Final rows after ensuring one unique file: {len(df_final)}")
print(f"Unique 'file' names after cleaning: {df_final['file'].nunique()}")

# ==== STEP 4: Save output ====
df_final.to_csv(OUTPUT_CSV, index=False)

print(f"Cleaned dataset saved to: {OUTPUT_CSV}")