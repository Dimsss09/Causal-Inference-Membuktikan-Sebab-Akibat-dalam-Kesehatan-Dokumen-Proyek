import os
import pandas as pd
import numpy as np
from dowhy import CausalModel
from sklearn.linear_model import LogisticRegression
from dag import init_dowhy_model, identify_causal_effect

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def calculate_e_value(rr):
    """
    Computes the E-value for a given Risk Ratio (VanderWeele & Ding, 2017).
    E-value = RR + sqrt(rr * (rr - 1))
    If rr < 1, invert it first.
    """
    if rr < 1:
        rr = 1 / rr
    e_val = rr + np.sqrt(rr * (rr - 1))
    return e_val

def run_refutations(df):
    """
    Initializes DoWhy model, estimates effect via IPW, and runs 3 refutation tests.
    """
    # 1. Initialize CausalModel and Identify Effect
    model = init_dowhy_model(df)
    identified_estimand = identify_causal_effect(model)
    
    # 2. Estimate Effect using DoWhy's Propensity Score Weighting
    print("Estimating effect using DoWhy IPW...")
    estimate = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.propensity_score_weighting",
        target_units="att",
        method_params={"weighting_scheme": "ips_weight"}
    )
    
    print(f"DoWhy IPW ATT Estimate: {estimate.value:+.4f}")
    
    # 3. Placebo Treatment Refuter
    # Replaces treatment with random dummy. Effect should go to 0.
    print("\nRunning Placebo Treatment Refuter (this may take a moment)...")
    refute_placebo = model.refute_estimate(
        identified_estimand,
        estimate,
        method_name="placebo_treatment_refuter",
        placebo_type="permute"
    )
    
    # 4. Random Common Cause Refuter
    # Adds a random variable as common cause. Effect should not change.
    print("\nRunning Random Common Cause Refuter...")
    refute_random = model.refute_estimate(
        identified_estimand,
        estimate,
        method_name="random_common_cause"
    )
    
    # 5. Data Subset Refuter
    # Estimates on a random subset of data. Effect should be stable.
    print("\nRunning Data Subset Refuter...")
    refute_subset = model.refute_estimate(
        identified_estimand,
        estimate,
        method_name="data_subset_refuter",
        subset_fraction=0.8
    )
    
    return estimate, refute_placebo, refute_random, refute_subset

def print_refutation_safely(refutation):
    """
    Prints refutation results safely handling Windows unicode print errors.
    """
    try:
        print(refutation)
    except UnicodeEncodeError:
        print(str(refutation).encode('ascii', errors='replace').decode('ascii'))

def main():
    encoded_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_encoded.csv")
    if not os.path.exists(encoded_path):
        raise FileNotFoundError(f"Encoded dataset not found at {encoded_path}. Run eda.py first.")
        
    df = pd.read_csv(encoded_path)
    
    # Run DoWhy Refutations
    estimate, refute_placebo, refute_random, refute_subset = run_refutations(df)
    
    print("\n=== HASIL UJI REFUTASI DOWHY ===")
    print("\n1. Placebo Treatment Refuter:")
    print_refutation_safely(refute_placebo)
    
    print("\n2. Random Common Cause Refuter:")
    print_refutation_safely(refute_random)
    
    print("\n3. Data Subset Refuter:")
    print_refutation_safely(refute_subset)
    
    # Run Sensitivity Analysis (E-value)
    # Using our Doubly Robust ATT of +3.94% (0.0394)
    # Observed treated mortality (p1) is 68.04% (0.6804)
    # Counterfactual control mortality (p0) is p1 - ATT = 68.04% - 3.94% = 64.10% (0.6410)
    p1 = 0.6804
    att_val = 0.0394
    p0 = p1 - att_val
    rr = p1 / p0
    e_val = calculate_e_value(rr)
    
    print("\n=== ANALISIS SENSITIVITAS (E-VALUE) ===")
    print(f"Mortality Treated (RHC) [Observed]: {p1*100:.2f}%")
    print(f"Mortality Control (No RHC) [Adjusted]: {p0*100:.2f}%")
    print(f"Risk Ratio (RR) adjusted: {rr:.4f}")
    print(f"E-value: {e_val:.4f}")
    print(f"Penjelasan: Dibutuhkan confounder tersembunyi yang memiliki Risk Ratio sebesar {e_val:.4f} terhadap treatment dan outcome untuk mematahkan efek kausal yang ditemukan.")

if __name__ == "__main__":
    main()
