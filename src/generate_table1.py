import os
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def calculate_smd(treated, control, is_categorical=False):
    """
    Calculates the Standardized Mean Difference (SMD) between treated and control groups.
    """
    mean_t = np.mean(treated)
    mean_c = np.mean(control)
    
    if is_categorical:
        # For proportions, standard formula: (p1 - p2) / sqrt((p1(1-p1) + p2(1-p2))/2)
        p1 = mean_t
        p2 = mean_c
        denom = np.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / 2.0)
    else:
        var_t = np.var(treated, ddof=1)
        var_c = np.var(control, ddof=1)
        denom = np.sqrt((var_t + var_c) / 2.0)
        
    if denom == 0:
        return 0.0
    return (mean_t - mean_c) / denom

def main():
    encoded_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_encoded.csv")
    matched_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_matched.csv")
    
    if not os.path.exists(encoded_path) or not os.path.exists(matched_path):
        print("Required datasets not found. Run estimators.py first.")
        return
        
    df_raw = pd.read_csv(encoded_path)
    df_matched = pd.read_csv(matched_path)
    
    # Selected key variables to show in Table 1
    # Formatting map for user-friendly display
    variables = [
        # Demographic
        ('age', 'Usia (Tahun)', False),
        ('sex_Female', 'Jenis Kelamin: Perempuan (%)', True),
        ('race_Black', 'Ras: Black (%)', True),
        ('race_White', 'Ras: White (%)', True),
        ('income_Under $11k', 'Pendapatan: < $11k (%)', True),
        # Physiological
        ('aps1', 'Skor APACHE III (Penyakit Akut)', False),
        ('meanbp1', 'Mean Blood Pressure (mmHg)', False),
        ('pafi1', 'PaO2/FiO2 Ratio (Oksigenasi)', False),
        ('crea1', 'Kadar Serum Kreatinin (Ginjal)', False),
        ('hema1', 'Kadar Hematokrit (%)', False),
        ('temp1', 'Suhu Tubuh (Celcius)', False),
        # Comorbidities
        ('card', 'Komorbid: Kardiovaskular (%)', True),
        ('resp', 'Komorbid: Respirasi (%)', True),
        ('renal', 'Komorbid: Renal/Ginjal (%)', True),
        ('liver', 'Komorbid: Liver (%)', True),
        ('ca_Yes', 'Komorbid: Kanker Akif (%)', True),
        # Primary Diagnosis
        ('cat1_MOSF w/Sepsis', 'Diagnosis: Gagal Organ Ganda & Sepsis (%)', True),
        ('cat1_COPD', 'Diagnosis: PPOK / Paru Kronis (%)', True),
        ('cat1_CHF', 'Diagnosis: Gagal Jantung Kongestif (%)', True),
        ('cat1_ARDS', 'Diagnosis: Gagal Napas Akut (ARDS) (%)', True),
    ]
    
    table1_rows = []
    
    for col, name, is_cat in variables:
        if col not in df_raw.columns:
            continue
            
        # 1. Raw Stats (Pre-match)
        raw_treated = df_raw[df_raw['treatment'] == 1][col]
        raw_control = df_raw[df_raw['treatment'] == 0][col]
        
        raw_mean_t = raw_treated.mean()
        raw_mean_c = raw_control.mean()
        raw_smd = calculate_smd(raw_treated.values, raw_control.values, is_cat)
        
        # 2. Matched Stats (Post-match)
        matched_treated = df_matched[df_matched['treatment'] == 1][col]
        matched_control = df_matched[df_matched['treatment'] == 0][col]
        
        match_mean_t = matched_treated.mean()
        match_mean_c = matched_control.mean()
        match_smd = calculate_smd(matched_treated.values, matched_control.values, is_cat)
        
        # Format display values (multiply proportions by 100 for percentage display)
        mult = 100.0 if is_cat else 1.0
        
        table1_rows.append({
            'Variabel Klinis & Demografi': name,
            'RHC Raw Mean': f"{raw_mean_t * mult:.2f}",
            'Kontrol Raw Mean': f"{raw_mean_c * mult:.2f}",
            'SMD Raw': f"{raw_smd:+.4f}",
            'RHC Matched Mean': f"{match_mean_t * mult:.2f}",
            'Kontrol Matched Mean': f"{match_mean_c * mult:.2f}",
            'SMD Matched': f"{match_smd:+.4f}"
        })
        
    table1_df = pd.DataFrame(table1_rows)
    output_path = os.path.join(PROJECT_ROOT, "data", "processed", "table1.csv")
    table1_df.to_csv(output_path, index=False)
    print(f"Table 1 generated and saved successfully to {output_path}")

if __name__ == "__main__":
    main()
