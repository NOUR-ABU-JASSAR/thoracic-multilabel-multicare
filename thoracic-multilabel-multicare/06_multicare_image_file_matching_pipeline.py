import pandas as pd
import shutil
from pathlib import Path

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent

MERGED_CSV = BASE_DIR / "data" / "xray_thorax_filtered" / "merged_all.csv"
IMAGES_DIR = BASE_DIR / "data" / "images"
OUTPUT_DIR = BASE_DIR / "data" / "xray_thorax_filtered" / "thorax_images"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === Load CSV and extract filenames ===
df = pd.read_csv(MERGED_CSV, dtype=str)

valid_files = set(
    Path(f).name.strip().lower()
    for f in df['file'].dropna()
)

print(f"Total unique filenames from 'file' column: {len(valid_files)}")

# === Match and copy .webp files ===
copied = 0
missing = []

for file_path in IMAGES_DIR.rglob("*.webp"):
    filename = file_path.name.lower()

    if filename in valid_files:
        shutil.copy2(file_path, OUTPUT_DIR / file_path.name)
        copied += 1
    else:
        missing.append(file_path.name)

print(f"Copied {copied} images to {OUTPUT_DIR}")
print(f"Unmatched expected files: {len(valid_files) - copied}")

# === Save logs ===
pd.Series(sorted(valid_files)).to_csv(OUTPUT_DIR / "expected_files.csv", index=False)
pd.Series(sorted(missing)).to_csv(OUTPUT_DIR / "skipped_files.csv", index=False)