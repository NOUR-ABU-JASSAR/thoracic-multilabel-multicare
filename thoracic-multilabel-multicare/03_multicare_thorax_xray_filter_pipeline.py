import pandas as pd
import numpy as np
import ast
from pathlib import Path

# === Configuration ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "xray_thorax_filtered"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === Helper Functions ===

def parse_column_to_list_of_dicts(df, col):
    """Parse strings in a dataframe column to list of dicts if needed."""
    return df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

def normalize_id(id_str, length=13):
    """
    Normalize IDs:
    - lowercase
    - strip whitespace
    - truncate to fixed length
    """
    if not isinstance(id_str, str):
        return None
    return id_str.lower().strip()[:length]


# === Step 1: Filter captions ===
def filter_captions():
    captions_path = DATA_DIR / "captions_and_labels.csv"
    captions_df = pd.read_csv(captions_path)

    required_cols = ['image_subtype', 'radiology_region', 'main_image']
    for col in required_cols:
        if col not in captions_df.columns:
            raise ValueError(f"Missing expected column '{col}'")

    captions_df['image_subtype'] = captions_df['image_subtype'].astype(str).str.lower()
    captions_df['radiology_region'] = captions_df['radiology_region'].astype(str).str.lower()

    filtered = captions_df[
        (captions_df['image_subtype'] == 'x_ray') &
        (captions_df['radiology_region'] == 'thorax')
    ].copy()

    filtered['main_image_id'] = filtered['main_image'].apply(lambda x: normalize_id(x))

    output_path = OUTPUT_DIR / "captions_filtered.csv"
    filtered.to_csv(output_path, index=False)

    print(f"Filtered captions: {len(filtered)} rows")
    print("Sample IDs:", filtered['main_image_id'].dropna().unique()[:10].tolist())

    return filtered


# === Step 2: Filter case_images ===
def filter_case_images(filtered_captions):
    case_images_path = DATA_DIR / "case_images.parquet"
    case_images_df = pd.read_parquet(case_images_path)

    case_images_df['case_images'] = case_images_df['case_images'].apply(
        lambda x: x.tolist() if isinstance(x, np.ndarray) else []
    )

    exploded = case_images_df.explode('case_images').reset_index(drop=True)

    case_image_dicts = exploded['case_images'].apply(lambda x: x if isinstance(x, dict) else {})
    case_image_details = pd.json_normalize(case_image_dicts)

    expanded = pd.concat([exploded.drop(columns=['case_images']), case_image_details], axis=1)

    expanded['norm_case_id'] = expanded['case_id'].astype(str).apply(lambda x: normalize_id(x))

    filtered_ids = set(filtered_captions['main_image_id'].dropna().unique())

    matched = expanded[expanded['norm_case_id'].isin(filtered_ids)].copy()

    print(f"Matched case_images rows: {len(matched)}")

    output_path = OUTPUT_DIR / "case_images_filtered.parquet"
    matched.to_parquet(output_path, index=False)

    return matched


# === Step 3: Filter cases ===
def filter_cases(filtered_case_ids):
    cases_path = DATA_DIR / "cases.parquet"
    cases_df = pd.read_parquet(cases_path)

    cases_df['cases'] = cases_df['cases'].apply(
        lambda x: x if isinstance(x, (list, tuple, np.ndarray)) else []
    )

    exploded = cases_df.explode('cases').reset_index(drop=True)

    def convert_to_dict(x):
        if isinstance(x, dict):
            return x
        return {}

    cases_details = pd.json_normalize(exploded['cases'].apply(convert_to_dict))
    expanded = pd.concat([exploded.drop(columns=['cases']), cases_details], axis=1)

    if 'case_id' not in expanded.columns:
        raise KeyError("case_id not found after processing")

    filtered_case_ids = set(str(x).lower() for x in filtered_case_ids if isinstance(x, str))

    filtered = expanded[
        expanded['case_id'].astype(str).str.lower().isin(filtered_case_ids)
    ].copy()

    output_path = OUTPUT_DIR / "cases_filtered.parquet"
    filtered.to_parquet(output_path, index=False)

    print(f"Filtered cases rows: {len(filtered)}")
    return filtered


# === Step 4: Filter metadata + abstracts ===
def filter_metadata_and_abstracts(filtered_article_ids):
    filtered_article_ids = set(filtered_article_ids)

    metadata = pd.read_parquet(DATA_DIR / "metadata.parquet")
    metadata_filtered = metadata[metadata['article_id'].isin(filtered_article_ids)]
    metadata_filtered.to_parquet(OUTPUT_DIR / "metadata_filtered.parquet", index=False)

    abstracts = pd.read_parquet(DATA_DIR / "abstracts.parquet")
    abstracts_filtered = abstracts[abstracts['article_id'].isin(filtered_article_ids)]
    abstracts_filtered.to_parquet(OUTPUT_DIR / "abstracts_filtered.parquet", index=False)

    print(f"Filtered metadata: {len(metadata_filtered)} rows")
    print(f"Filtered abstracts: {len(abstracts_filtered)} rows")


# === Main ===
def main():
    filtered_captions = filter_captions()
    matched_case_images = filter_case_images(filtered_captions)

    if matched_case_images.empty:
        print("No matches found. Stopping pipeline.")
        return

    filtered_case_ids = matched_case_images['case_id'].dropna().unique()
    filtered_article_ids = matched_case_images['article_id'].dropna().unique()

    filter_cases(filtered_case_ids)
    filter_metadata_and_abstracts(filtered_article_ids)

    print(f"\nAll outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()