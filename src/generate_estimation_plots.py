import os
import pandas as pd
import numpy as np
from plots import plot_propensity_score_distribution, calculate_smd, plot_love_plot_comparison
from dag import get_confounders

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_plots():
    estimated_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_estimated.csv")
    matched_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_matched.csv")
    
    if not os.path.exists(estimated_path) or not os.path.exists(matched_path):
        raise FileNotFoundError("Run estimators.py first to generate datasets.")
        
    df_est = pd.read_csv(estimated_path)
    df_match = pd.read_csv(matched_path)
    
    # 1. Generate Propensity Score Overlap Plot
    plot_propensity_score_distribution(df_est, ps_col='propensity_score')
    
    # 2. Get list of confounders
    confounders = get_confounders(df_est)
    
    # 3. Calculate unadjusted SMDs
    print("Calculating unadjusted SMDs...")
    unadjusted_smds = calculate_smd(df_est, confounders)
    
    # 4. Calculate matched SMDs
    print("Calculating matched SMDs...")
    matched_smds = calculate_smd(df_match, confounders)
    
    # 5. Generate Love Plot Comparison
    plot_love_plot_comparison(
        unadjusted_smds, 
        matched_smds, 
        method_label="Propensity Score Matching (1:1)",
        output_path=os.path.join(PROJECT_ROOT, "reports", "figures", "06_love_plot_comparison.png")
    )
    
    # Let's count how many covariates are still imbalanced (|SMD| > 0.1) after matching
    imbalanced_before = (unadjusted_smds['smd'].abs() > 0.1).sum()
    imbalanced_after = (matched_smds['smd'].abs() > 0.1).sum()
    print(f"Number of imbalanced covariates before matching: {imbalanced_before}")
    print(f"Number of imbalanced covariates after matching: {imbalanced_after}")
    
    return imbalanced_before, imbalanced_after

if __name__ == "__main__":
    generate_plots()
