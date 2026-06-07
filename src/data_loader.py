import os
import urllib.request
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def download_data(raw_data_dir=None):
    """
    Downloads the Right Heart Catheterization (RHC) dataset from Vanderbilt Biostatistics.
    """
    if raw_data_dir is None:
        raw_data_dir = os.path.join(PROJECT_ROOT, "data", "raw")
        
    os.makedirs(raw_data_dir, exist_ok=True)
    target_path = os.path.join(raw_data_dir, "rhc.csv")
    url = "https://hbiostat.org/data/repo/rhc.csv"
    
    if not os.path.exists(target_path):
        print(f"Downloading RHC dataset from {url}...")
        urllib.request.urlretrieve(url, target_path)
        print(f"Downloaded and saved to {target_path}")
    else:
        print(f"RHC dataset already exists at {target_path}")
    return target_path

def load_and_preprocess_data(csv_path=None, processed_data_dir=None):
    """
    Loads the RHC dataset and performs basic preprocessing.
    - Treatment (swang1): 'RHC' -> 1, 'No RHC' -> 0
    - Outcome (death): 'Yes' -> 1, 'No' -> 0
    """
    if csv_path is None:
        csv_path = os.path.join(PROJECT_ROOT, "data", "raw", "rhc.csv")
    if processed_data_dir is None:
        processed_data_dir = os.path.join(PROJECT_ROOT, "data", "processed")
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Preprocess Treatment
    if 'swang1' in df.columns:
        df['treatment'] = df['swang1'].map({'RHC': 1, 'No RHC': 0})
    else:
        raise ValueError("Treatment column 'swang1' not found in dataset.")
        
    # Preprocess Outcome (death: yes/no)
    if 'death' in df.columns:
        df['outcome'] = df['death'].map({'Yes': 1, 'No': 0})
    elif 'dth30' in df.columns:
        df['outcome'] = df['dth30'].map({'Yes': 1, 'No': 0})
    else:
        # Fallback search for death indicators
        raise ValueError("Outcome column (death) not found in dataset.")
    
    # Let's inspect other common columns
    # We want to identify candidate confounders.
    # Typically: age, sex, race, edu, income, nisa, hema, seps, trauma, ortho, card, resp, neuro, gastr, renal, meta, ...
    # Let's keep all variables but clean binary/categorical ones if needed.
    
    # Save the processed dataset
    os.makedirs(processed_data_dir, exist_ok=True)
    processed_path = os.path.join(processed_data_dir, "rhc_processed.csv")
    df.to_csv(processed_path, index=False)
    print(f"Processed dataset saved to {processed_path}")
    
    # Let's print out basic info
    print(f"Dataset shape: {df.shape}")
    print(f"Treatment distribution:\n{df['treatment'].value_counts(dropna=False)}")
    print(f"Outcome distribution:\n{df['outcome'].value_counts(dropna=False)}")
    
    return df

if __name__ == "__main__":
    raw_path = download_data()
    df = load_and_preprocess_data(raw_path)
