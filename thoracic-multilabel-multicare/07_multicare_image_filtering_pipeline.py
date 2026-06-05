import pandas as pd
import shutil
import re
from pathlib import Path

# === Paths  ===
BASE_DIR = Path(__file__).resolve().parent.parent

MERGED_CSV = BASE_DIR / "data" / "xray_thorax_filtered" / "merged_all.csv"
IMAGES_DIR = BASE_DIR / "data" / "images"

INTERMEDIATE_DIR = BASE_DIR / "data" / "xray_thorax_filtered" / "thorax_images"
FINAL_DIR = BASE_DIR / "data" / "xray_thorax_filtered" / "final_images"

INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

# === Load CSV ===
df = pd.read_csv(MERGED_CSV, dtype=str)

# === Helper ===
def strip_suffix(pid):
    return re.sub(r"_\d+$", "", str(pid).strip().lower())

# === Step 1: Heuristic match by patient_id ===
base_ids = set(strip_suffix(pid) for pid in df['patient_id'].dropna())
matches = []

for file_path in IMAGES_DIR.rglob("*.webp"):
    stem = file_path.stem.lower()

    for base in base_ids:
        if stem.startswith(base):
            dst = INTERMEDIATE_DIR / file_path.name
            shutil.copy2(file_path, dst)
            matches.append({
                "base_patient_id": base,
                "matched_file": file_path.name
            })
            break

print(f"[Step 1] Heuristic matched images: {len(matches)}")

# === Step 2: Filter by dataset stems ===
columns_to_check = [
    "main_image", "file_id", "file", "image_component",
    "patient_id", "license", "file_size", "caption",
    "case_substring", "image_type", "image_subtype",
    "radiology_region", "radiology_region_granular",
    "radiology_view", "ml_labels_for_supervised_classification",
    "gt_labels_for_semisupervised_classification"
]

stems = set()

for _, row in df.iterrows():
    for col in columns_to_check:
        val = str(row.get(col, "")).strip()
        if val and val.lower() != "nan":
            stem = val.rsplit(".", 1)[0].lower()
            stems.add(stem)

kept, removed = [], []

for file_path in INTERMEDIATE_DIR.glob("*.webp"):
    if file_path.stem.lower() in stems:
        shutil.copy2(file_path, FINAL_DIR / file_path.name)
        kept.append(file_path.name)
    else:
        removed.append(file_path.name)

print(f"[Step 2] Final kept images: {len(kept)}")
print(f"[Step 2] Removed images: {len(removed)}")

# === Save logs ===
pd.DataFrame(matches).to_csv(INTERMEDIATE_DIR / "patient_id_matches.csv", index=False)

(FINAL_DIR / "kept_images.txt").write_text("\n".join(kept))
(FINAL_DIR / "removed_images.txt").write_text("\n".join(removed))