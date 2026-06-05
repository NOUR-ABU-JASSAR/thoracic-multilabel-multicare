import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from pathlib import Path

# =========================================================
# Paths 
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent  # repo root
DATA_DIR = BASE_DIR / "data" / "xray_thorax_filtered"

LABELS_FILE = DATA_DIR / "merged_all_cleaned_scanned_per_row_labels.csv"

# =========================================================
# Output folder
# =========================================================
OUTPUT_DIR = BASE_DIR / "analysis_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================================================
# Load dataset
# =========================================================
df = pd.read_csv(LABELS_FILE)

# --- Detect label columns ---
exclude_cols = ["image", "id", "filename", "path", "file", "patient_id", "case_text"]
label_cols = [c for c in df.columns if c.lower() not in exclude_cols]

# --- Ensure numeric binary format ---
df[label_cols] = df[label_cols].apply(pd.to_numeric, errors="coerce").fillna(0).astype(int)

# =========================================================
# 1. Label frequency counts
# =========================================================
label_counts = df[label_cols].sum().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(
    x=label_counts.values,
    y=label_counts.index,
    hue=label_counts.index,
    palette="viridis",
    legend=False
)
plt.title("Number of Images per Label")
plt.xlabel("Count")
plt.ylabel("Label")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "label_counts.png")
plt.close()

# =========================================================
# 2. Co-occurrence matrix
# =========================================================
co_matrix = df[label_cols].T.dot(df[label_cols])

np.fill_diagonal(co_matrix.values, label_counts.values)

plt.figure(figsize=(12, 10))
sns.heatmap(co_matrix, cmap="YlGnBu", linewidths=0.5)
plt.title("Label Co-occurrence Heatmap")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "co_occurrence_heatmap.png")
plt.close()

# =========================================================
# 3. Top label pairs
# =========================================================
pair_counts = []
for i, col1 in enumerate(label_cols):
    for col2 in label_cols[i + 1:]:
        count = ((df[col1] == 1) & (df[col2] == 1)).sum()
        pair_counts.append((col1, col2, count))

pair_df = pd.DataFrame(pair_counts, columns=["Label1", "Label2", "Count"])
pair_df = pair_df.sort_values(by="Count", ascending=False)

top_pairs = pair_df.head(10).copy()
top_pairs["pair"] = top_pairs["Label1"] + " + " + top_pairs["Label2"]

plt.figure(figsize=(10, 6))
sns.barplot(x="Count", y="pair", data=top_pairs, color="steelblue")
plt.title("Top 10 Most Frequent Label Pairs")
plt.xlabel("Count")
plt.ylabel("Label Pair")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "top10_pairs.png")
plt.close()

# =========================================================
# 4. Label density per image
# =========================================================
df["num_labels"] = df[label_cols].sum(axis=1)

plt.figure(figsize=(8, 6))
sns.histplot(
    df["num_labels"],
    bins=range(0, df["num_labels"].max() + 2),
    kde=False,
    color="steelblue"
)
plt.title("Distribution of Number of Labels per Image")
plt.xlabel("Number of Labels per Image")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "labels_per_image_distribution.png")
plt.close()

# =========================================================
# 5. Save outputs
# =========================================================
excel_path = OUTPUT_DIR / "label_analysis.xlsx"

with pd.ExcelWriter(excel_path) as writer:
    label_counts.to_frame(name="Count").to_excel(writer, sheet_name="Label Counts")
    pair_df.to_excel(writer, sheet_name="Co-Label Pairs", index=False)
    df[["num_labels"]].to_excel(writer, sheet_name="Labels Per Image", index=False)
    co_matrix.to_excel(writer, sheet_name="Co-Occurrence Matrix")

print(f"Analysis complete. Outputs saved to: {OUTPUT_DIR}")
print(f"Excel report: {excel_path}")