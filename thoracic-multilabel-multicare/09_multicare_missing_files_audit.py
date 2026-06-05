import pandas as pd
from pathlib import Path

# === Paths  ===
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "data" / "xray_thorax_filtered" / "merged_all.csv"
IMAGES_DIR = BASE_DIR / "data" / "images"

# === Load CSV ===
df = pd.read_csv(CSV_PATH, dtype=str)

# === Extract and clean file names ===
df['file_clean'] = (
    df['file']
    .fillna("")
    .astype(str)
    .apply(lambda x: Path(x).name.strip().lower())
)

valid_files = df[df['file_clean'] != ""]

print(f"Total rows with non-empty 'file': {len(valid_files)}")

# === Build set of existing images for fast lookup ===
image_files = {f.name.lower() for f in IMAGES_DIR.rglob("*") if f.is_file()}

# === Check missing files ===
missing = [
    fname for fname in valid_files['file_clean']
    if fname not in image_files
]

print(f"Missing files: {len(missing)}")

# === Save missing list ===
if missing:
    pd.Series(missing).to_csv(
        BASE_DIR / "data" / "xray_thorax_filtered" / "missing_from_images_dir.csv",
        index=False
    )