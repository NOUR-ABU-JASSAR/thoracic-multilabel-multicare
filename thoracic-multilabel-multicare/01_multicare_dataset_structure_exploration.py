import pandas as pd
import ast
from pathlib import Path

# Dataset directory
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def parse_column_to_list_of_dicts(df, col):
    return df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# 1. captions_and_labels.csv sample
captions_df = pd.read_csv(DATA_DIR / "captions_and_labels.csv")
print("=== Captions Sample ===")
print(captions_df.head(3)[['file_id', 'file', 'patient_id', 'image_subtype', 'radiology_region']])

# 2. case_images.parquet sample
case_images_df = pd.read_parquet(DATA_DIR / "case_images.parquet")
case_images_df['case_images'] = parse_column_to_list_of_dicts(case_images_df, 'case_images')

print("\n=== case_images.parquet sample (exploded first element) ===")
first_case_images = case_images_df.iloc[0]['case_images']
print(type(first_case_images), len(first_case_images))
print(first_case_images[0])

# Show first nested case_image_list entry
print("\nFirst case_image_list entry:")
print(first_case_images[0]['case_image_list'][0])

# 3. cases.parquet sample
cases_df = pd.read_parquet(DATA_DIR / "cases.parquet")
cases_df['cases'] = parse_column_to_list_of_dicts(cases_df, 'cases')

print("\n=== cases.parquet sample (exploded first element) ===")
first_cases = cases_df.iloc[0]['cases']
print(type(first_cases), len(first_cases))
print(first_cases[0])

# 4. metadata.parquet sample
metadata_df = pd.read_parquet(DATA_DIR / "metadata.parquet")
print("\n=== metadata.parquet sample ===")
print(metadata_df.head(3))

# 5. abstracts.parquet sample
abstracts_df = pd.read_parquet(DATA_DIR / "abstracts.parquet")
print("\n=== abstracts.parquet sample ===")
print(abstracts_df.head(3))