import os
import pandas as pd
import numpy as np
from plots import plot_treatment_distribution, plot_outcome_by_treatment, calculate_smd, plot_love_plot

# Set project root path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_eda():
    processed_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_processed.csv")
    if not os.path.exists(processed_path):
        raise FileNotFoundError(f"Processed dataset not found at {processed_path}. Run data_loader.py first.")
        
    df = pd.read_csv(processed_path)
    
    print("Running EDA...")
    
    # 1. Generate Basic distribution plots
    plot_treatment_distribution(df)
    plot_outcome_by_treatment(df)
    
    # 2. Check and record missing values
    missing_info = df.isnull().sum()
    missing_summary = missing_info[missing_info > 0].to_dict()
    
    # 3. Identify and process covariates (confounders)
    # Define numeric confounders
    num_confounders = [
        'age', 'edu', 'surv2md1', 'das2d3pc', 'aps1', 'scoma1', 'meanbp1', 
        'wblc1', 'hrt1', 'resp1', 'temp1', 'pafi1', 'alb1', 'hema1', 
        'bili1', 'crea1', 'sod1', 'pot1', 'paco21', 'ph1', 'wtkilo1'
    ]
    
    # Define categorical confounders
    cat_confounders = ['cat1', 'sex', 'race', 'income', 'ninsclas', 'dnr1', 'ca', 'cat2']
    
    # Organ system failure flags (mostly binary 1/0 or yes/no represented as strings/ints)
    # Let's map any yes/no in other columns to 1/0
    binary_cols = ['cardiohx', 'chfhx', 'dementhx', 'psychhx', 'chrpulhx', 
                   'renalhx', 'liverhx', 'gibledhx', 'malighx', 'immunhx', 
                   'transhx', 'amihx', 'resp', 'card', 'neuro', 'gastr', 
                   'renal', 'meta', 'hema', 'seps', 'trauma', 'ortho']
    
    # Map binary columns to 1/0 if they contain Yes/No, and convert to integer
    for col in binary_cols:
        if df[col].dtype in ['object', 'str', 'string'] or isinstance(df[col].dtype, pd.StringDtype) or hasattr(df[col], 'str'):
            df[col] = df[col].map({'Yes': 1, 'No': 0, 'yes': 1, 'no': 0})
        df[col] = df[col].astype(int)
    
    # One-hot encode categorical confounders
    df_encoded = pd.get_dummies(df, columns=cat_confounders, drop_first=True)
    
    # Get all dummy column names created
    dummy_cols = [col for col in df_encoded.columns if any(col.startswith(cat + '_') for cat in cat_confounders)]
    
    # Total set of confounder columns for analysis
    all_covariates = num_confounders + binary_cols + dummy_cols
    
    # Convert bool columns to int for SMD calculation
    for col in dummy_cols:
        df_encoded[col] = df_encoded[col].astype(int)
        
    # 4. Calculate Standardized Mean Differences (SMD) before adjustment
    smd_df = calculate_smd(df_encoded, all_covariates)
    
    # Save Love Plot
    plot_love_plot(smd_df)
    
    # Save the dummy-encoded dataset for modeling
    encoded_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_encoded.csv")
    df_encoded.to_csv(encoded_path, index=False)
    print(f"Encoded dataset (for modeling) saved to {encoded_path}")
    
    # 5. Compile a Markdown report summary
    report_path = os.path.join(PROJECT_ROOT, "reports", "results.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    # Calculate key statistics
    total_patients = len(df)
    rhc_count = (df['treatment'] == 1).sum()
    control_count = (df['treatment'] == 0).sum()
    rhc_pct = rhc_count / total_patients * 100
    control_pct = control_count / total_patients * 100
    
    mortality_rhc = df[df['treatment'] == 1]['outcome'].mean() * 100
    mortality_control = df[df['treatment'] == 0]['outcome'].mean() * 100
    naive_difference = mortality_rhc - mortality_control
    
    # Find top imbalanced covariates (SMD > 0.1)
    imbalanced_smd = smd_df[smd_df['smd'].abs() > 0.1].copy()
    imbalanced_smd['abs_smd'] = imbalanced_smd['smd'].abs()
    imbalanced_smd = imbalanced_smd.sort_values(by='abs_smd', ascending=False)
    
    with open(report_path, "w") as f:
        f.write("# Ringkasan Analisis Causal Inference: RHC & Mortalitas ICU\n\n")
        f.write("## Hasil Exploratory Data Analysis (EDA) - Fase 1\n\n")
        f.write(f"- **Total Sampel:** {total_patients} pasien ICU.\n")
        f.write(f"  - **Kelompok Treatment (RHC):** {rhc_count} pasien ({rhc_pct:.2f}%).\n")
        f.write(f"  - **Kelompok Kontrol (No RHC):** {control_count} pasien ({control_pct:.2f}%).\n\n")
        
        f.write("### Perbandingan Naif (Korelasi Awal)\n")
        f.write(f"- **Tingkat Mortalitas 30 Hari - Kelompok RHC:** {mortality_rhc:.2f}%\n")
        f.write(f"- **Tingkat Mortalitas 30 Hari - Kelompok Kontrol:** {mortality_control:.2f}%\n")
        f.write(f"- **Perbedaan Efek Naif (Naive Risk Difference):** {naive_difference:+.2f}% (RHC tampak meningkatkan kematian)\n\n")
        
        f.write("> **Catatan:** Perbedaan naif ini sangat bias karena *confounding by indication*—pasien yang dipasang RHC umumnya berada dalam kondisi klinis yang lebih parah.\n\n")
        
        f.write("### Pemeriksaan Missing Values\n")
        if missing_summary:
            f.write("Ditemukan beberapa nilai yang hilang di dataset:\n")
            for col, count in missing_summary.items():
                f.write(f"- Kolom `{col}`: {count} nilai kosong.\n")
        else:
            f.write("Tidak ada missing values pada kovariat utama.\n")
        f.write("\n")
        
        f.write("### Keseimbangan Kovariat Awal (Covariate Balance)\n")
        f.write(f"Ditemukan **{len(imbalanced_smd)}** kovariat yang memiliki Standardized Mean Difference (SMD) melebihi batas batas aman (|SMD| > 0.1), yang menunjukkan ketidakseimbangan parah sebelum penyesuaian kausal.\n\n")
        
        f.write("#### Top 10 Kovariat Paling Tidak Seimbang:\n\n")
        f.write("| Kovariat | SMD (Sebelum Penyesuaian) | Penjelasan Klinis |\n")
        f.write("| --- | --- | --- |\n")
        
        # Populate top 10 imbalanced features with SMDs
        for i, row in imbalanced_smd.head(10).iterrows():
            cov_name = row['covariate']
            smd_val = row['smd']
            # Simple manual explanation for some key columns
            desc = "Karakteristik fisiologis / tingkat keparahan"
            if 'aps1' in cov_name:
                desc = "Skor APACHE III (keparahan penyakit - pasien RHC lebih sakit)"
            elif 'surv2md1' in cov_name:
                desc = "Estimasi probabilitas kelangsungan hidup 2 bulan dari SUPPORT model (RHC lebih rendah)"
            elif 'dnr1' in cov_name:
                desc = "Instruksi Do Not Resuscitate (DNR) hari ke-1"
            elif 'cat1' in cov_name:
                desc = "Kategori penyakit utama"
            elif 'meanbp1' in cov_name:
                desc = "Tekanan darah rata-rata hari ke-1"
            elif 'pafi1' in cov_name:
                desc = "Rasio PaO2/FIO2 (kadar oksigenasi darah)"
            elif 'age' in cov_name:
                desc = "Usia pasien"
            elif 'crea1' in cov_name:
                desc = "Kadar kreatinin serum (fungsi ginjal)"
            elif 'seps' in cov_name:
                desc = "Mengalami sepsis"
            elif 'das2d3pc' in cov_name:
                desc = "Skor aktivitas DASI (kemampuan fungsional)"
                
            f.write(f"| `{cov_name}` | {smd_val:+.4f} | {desc} |\n")
            
    print(f"EDA Summary Report saved to {report_path}")

if __name__ == "__main__":
    run_eda()
