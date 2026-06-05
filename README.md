# Thoracic-Multilabel-Multicare
Curated thoracic subset from MultiCaRe for multi‑label disease classification – code and subset manifest
# Curated Thoracic Subset from MultiCaRe for Multi-Label Chest X-Ray Disease Classification



## Overview



This repository contains code and metadata for the **Curated Thoracic Subset from MultiCaRe**, a chest X-ray dataset designed for **multi-label thoracic disease classification**.



The dataset is derived from the original MultiCaRe dataset:

https://zenodo.org/records/13936721



It includes only **thorax-focused chest X-ray cases** and provides structured labels extracted from clinical reports using a **negation-aware NLP pipeline**.



---



## Dataset Citation



If you use this dataset, please cite:



> ABU JASSAR, N., ALMALKAWI, I., Al-Hammouri, M., & Al Bataineh, A.  

> *Curated Thoracic Subset from MultiCaRe for Multi-Label Chest X-Ray Disease Classification*.  

> Zenodo (2026). https://doi.org/10.5281/zenodo.20548927



---



## License



This dataset is released under:



**Creative Commons Attribution Non Commercial Share Alike 4.0 International (CC BY-NC-SA 4.0)**



https://creativecommons.org/licenses/by-nc-sa/4.0/



It inherits the same licensing terms from the original MultiCaRe dataset.



---



## Dataset Description



This subset was created through the following curation steps:



- Filtering original MultiCaRe data to retain only:

  - Chest X-ray images

  - Thoracic region cases

- Extracting labels from clinical case reports 

- Using a **negation-aware NLP pipeline** to improve label accuracy

- Preserving full metadata for reproducibility



---



## Primary Labels (16 classes)



The main benchmark labels are:



- pneumonia  

- pleural_effusion  

- atelectasis  

- pneumothorax  

- cardiomegaly  

- pulmonary_edema  

- lung_mass_or_cancer  

- interstitial_lung_disease  

- bronchitis  

- emphysema  

- tuberculosis  

- covid19  

- congestive_heart_failure  

- heart_failure  

- congenital_heart_disease  

- asthma  



---



## Additional Labels



Additional clinical labels (not used as primary benchmark targets) may also appear in the dataset:



- anemia  

- seizure  

- stroke  

- and others



---



## Repository Contents



This repository includes:



### Filtered Dataset

- `case_images_filtered.parquet`

- `cases_filtered.parquet`

- `metadata_filtered.parquet`

- `abstracts_filtered.parquet`

- `captions_filtered.csv`



### Merged Dataset

- `merged_all_cleaned.parquet`

- `merged_all_cleaned_Preserves_all_original_columns.csv`



### Label Extraction Outputs

- `merged_all_cleaned_scanned_per_row_labels.csv`

- `merged_all_cleaned_scanned_term_counts.csv`

- `merged_all_cleaned_scanned_ngram_candidates_unigrams.csv`

- `merged_all_cleaned_scanned_ngram_candidates_bigrams.csv`

- `merged_all_cleaned_scanned_ngram_candidates_trigrams.csv`

- `merged_all_cleaned_scanned_cooccurrence_matrix.csv`



### Data Quality Files

- `duplicate_files_exact.csv`

- `duplicate_files.csv`



---



## Reproducibility



All filtering, merging, and label extraction steps can be reproduced using the Python scripts in the `/scripts` directory.



Typical pipeline:



1. Filter thoracic X-ray cases  

2. Match and align case-images  

3. Merge metadata tables  

4. Clean duplicates  

5. Extract labels using NLP pipeline  

6. Generate statistical analysis outputs  



---



## Requirements



Install dependencies using:



```bash

pip install -r requirements.txt
