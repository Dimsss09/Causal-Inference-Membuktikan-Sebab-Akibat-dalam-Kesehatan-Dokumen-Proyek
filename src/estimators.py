import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from dag import get_confounders

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def estimate_propensity_scores(df, verbose=True):
    """
    Fits a logistic regression to predict treatment using all confounders.
    Adds the 'propensity_score' column to the dataframe in-place.
    """
    confounders = get_confounders(df)
    X = df[confounders]
    y = df['treatment']
    
    # Scale numerical features to improve convergence
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train propensity score model
    model = LogisticRegression(max_iter=2000, random_state=42)
    model.fit(X_scaled, y)
    
    # Add propensity scores to dataframe
    df['propensity_score'] = model.predict_proba(X_scaled)[:, 1]
    if verbose:
        print(f"Propensity scores estimated. Range: [{df['propensity_score'].min():.4f}, {df['propensity_score'].max():.4f}]")
    return df

def estimate_naive_effect(df, verbose=True):
    """
    Computes the naive risk difference (difference in mortality rates).
    """
    p_treat = df[df['treatment'] == 1]['outcome'].mean()
    p_control = df[df['treatment'] == 0]['outcome'].mean()
    
    naive_ate = p_treat - p_control
    if verbose:
        print(f"Naive ATE (Risk Difference): {naive_ate:+.4f} (RHC: {p_treat:.4f}, No RHC: {p_control:.4f})")
    return {
        'method': 'Naive (Korelasi)',
        'ATE': naive_ate,
        'ATT': naive_ate
    }

def estimate_effect_psm(df, caliper=0.2, verbose=True):
    """
    Performs 1:1 Propensity Score Matching without replacement.
    Estimates ATT (Average Treatment Effect on the Treated).
    """
    treated = df[df['treatment'] == 1].copy()
    control = df[df['treatment'] == 0].copy()
    
    # Convert propensity scores to log-odds (logit)
    def logit(p):
        p_clipped = np.clip(p, 1e-6, 1 - 1e-6)
        return np.log(p_clipped / (1 - p_clipped))
        
    treated['ps_logit'] = logit(treated['propensity_score'])
    control['ps_logit'] = logit(control['propensity_score'])
    
    # Calculate caliper width based on standard deviation of logit of PS in treated group
    caliper_width = caliper * treated['ps_logit'].std()
    if np.isnan(caliper_width) or caliper_width == 0:
        caliper_width = 0.2  # Fallback caliper
    
    # Match using NearestNeighbors
    nn = NearestNeighbors(n_neighbors=1, metric='manhattan')
    nn.fit(control['ps_logit'].values.reshape(-1, 1))
    
    distances, indices = nn.kneighbors(treated['ps_logit'].values.reshape(-1, 1))
    
    matched_control_indices = []
    valid_treated_indices = []
    
    for i in range(len(treated)):
        if distances[i][0] <= caliper_width:
            matched_control_indices.append(control.index[indices[i][0]])
            valid_treated_indices.append(treated.index[i])
            
    # If no matches found, fallback to closest without caliper
    if len(valid_treated_indices) == 0:
        for i in range(len(treated)):
            matched_control_indices.append(control.index[indices[i][0]])
            valid_treated_indices.append(treated.index[i])
            
    matched_treated_df = df.loc[valid_treated_indices]
    matched_control_df = df.loc[matched_control_indices]
    
    att = matched_treated_df['outcome'].mean() - matched_control_df['outcome'].mean()
    if verbose:
        print(f"PSM matched: {len(valid_treated_indices)} out of {len(treated)} treated patients ({len(valid_treated_indices)/len(treated)*100:.1f}%)")
        print(f"PSM ATT: {att:+.4f}")
        
    matched_df = pd.concat([matched_treated_df, matched_control_df])
    return att, matched_df

def estimate_effect_ipw(df, verbose=True):
    """
    Estimates ATE and ATT using Inverse Probability Weighting (IPW) with stabilized weights.
    """
    ps = np.clip(df['propensity_score'].values, 1e-4, 1 - 1e-4)
    T = df['treatment'].values
    Y = df['outcome'].values
    
    # Weights for ATE and ATT
    w_ate = T / ps + (1 - T) / (1 - ps)
    w_att = T + (ps * (1 - T)) / (1 - ps)
    
    # Weighted outcomes
    ate = np.sum((T * Y) / ps) / np.sum(T / ps) - np.sum(((1 - T) * Y) / (1 - ps)) / np.sum((1 - T) / (1 - ps))
    att = np.sum(T * Y) / np.sum(T) - np.sum((ps * (1 - T) * Y) / (1 - ps)) / np.sum((ps * (1 - T)) / (1 - ps))
    
    if verbose:
        print(f"IPW ATE: {ate:+.4f} | ATT: {att:+.4f}")
    return ate, att, w_ate, w_att

def estimate_effect_doubly_robust(df, verbose=True):
    """
    Estimates ATE and ATT using Doubly Robust (AIPW) Estimation.
    """
    confounders = get_confounders(df)
    X = df[confounders]
    T = df['treatment'].values
    Y = df['outcome'].values
    ps = np.clip(df['propensity_score'].values, 1e-4, 1 - 1e-4)
    
    # Train outcome models
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model_y1 = LogisticRegression(max_iter=2000, random_state=42)
    model_y1.fit(X_scaled[T == 1], Y[T == 1])
    
    model_y0 = LogisticRegression(max_iter=2000, random_state=42)
    model_y0.fit(X_scaled[T == 0], Y[T == 0])
    
    mu_1 = model_y1.predict_proba(X_scaled)[:, 1]
    mu_0 = model_y0.predict_proba(X_scaled)[:, 1]
    
    # DR ATE
    dr_ate = np.mean(
        (mu_1 + (T * (Y - mu_1)) / ps) - 
        (mu_0 + ((1 - T) * (Y - mu_0)) / (1 - ps))
    )
    
    # DR ATT
    n_t = np.sum(T)
    dr_att = np.sum(
        T * Y - (T * mu_0 + (ps * (1 - T) * (Y - mu_0)) / (1 - ps))
    ) / n_t
    
    if verbose:
        print(f"Doubly Robust ATE: {dr_ate:+.4f} | ATT: {dr_att:+.4f}")
    return dr_ate, dr_att

def bootstrap_confidence_intervals(df, n_bootstrap=100):
    """
    Computes 95% confidence intervals and standard errors for ATE/ATT of all estimators.
    """
    print(f"Running Bootstrap standard error estimation (iterations={n_bootstrap})...")
    
    naive_ates = []
    psm_atts = []
    ipw_ates = []
    ipw_atts = []
    dr_ates = []
    dr_atts = []
    
    for b in range(n_bootstrap):
        # Sample with replacement
        boot_df = df.sample(frac=1.0, replace=True, random_state=b)
        
        try:
            boot_df = estimate_propensity_scores(boot_df, verbose=False)
            
            # Naive
            p_t = boot_df[boot_df['treatment'] == 1]['outcome'].mean()
            p_c = boot_df[boot_df['treatment'] == 0]['outcome'].mean()
            naive_ates.append(p_t - p_c)
            
            # PSM
            psm_val, _ = estimate_effect_psm(boot_df, verbose=False)
            psm_atts.append(psm_val)
            
            # IPW
            ipw_ate_val, ipw_att_val, _, _ = estimate_effect_ipw(boot_df, verbose=False)
            ipw_ates.append(ipw_ate_val)
            ipw_atts.append(ipw_att_val)
            
            # Doubly Robust
            dr_ate_val, dr_att_val = estimate_effect_doubly_robust(boot_df, verbose=False)
            dr_ates.append(dr_ate_val)
            dr_atts.append(dr_att_val)
        except Exception as e:
            # Skip iterations that fail (e.g. singular matrix, very rare)
            continue
            
        if (b + 1) % 20 == 0:
            print(f"Bootstrap progress: {b + 1}/{n_bootstrap}")
            
    def get_summary(estimates_list):
        if not estimates_list:
            return np.nan, np.nan, np.nan
        arr = np.array(estimates_list)
        se = np.std(arr)
        ci_lower = np.percentile(arr, 2.5)
        ci_upper = np.percentile(arr, 97.5)
        return se, ci_lower, ci_upper

    return {
        'naive_ate': get_summary(naive_ates),
        'psm_att': get_summary(psm_atts),
        'ipw_ate': get_summary(ipw_ates),
        'ipw_att': get_summary(ipw_atts),
        'dr_ate': get_summary(dr_ates),
        'dr_att': get_summary(dr_atts)
    }

def run_all_estimators(n_bootstrap=100):
    """
    Loads data, runs all estimators, calculates bootstrap CIs, and returns summary.
    """
    encoded_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_encoded.csv")
    if not os.path.exists(encoded_path):
        raise FileNotFoundError(f"Encoded dataset not found at {encoded_path}. Run eda.py first.")
        
    df = pd.read_csv(encoded_path)
    
    # 1. Point Estimates
    df = estimate_propensity_scores(df, verbose=True)
    naive_res = estimate_naive_effect(df, verbose=True)
    psm_att, matched_df = estimate_effect_psm(df, verbose=True)
    ipw_ate, ipw_att, w_ate, w_att = estimate_effect_ipw(df, verbose=True)
    dr_ate, dr_att = estimate_effect_doubly_robust(df, verbose=True)
    
    # Save datasets
    df['weights_ate'] = w_ate
    df['weights_att'] = w_att
    df.to_csv(os.path.join(PROJECT_ROOT, "data", "processed", "rhc_estimated.csv"), index=False)
    matched_df.to_csv(os.path.join(PROJECT_ROOT, "data", "processed", "rhc_matched.csv"), index=False)
    
    # 2. Bootstrap Confidence Intervals
    boot_ci = bootstrap_confidence_intervals(df, n_bootstrap=n_bootstrap)
    
    # Create final summary DataFrame
    summary_data = [
        {
            'Metode': 'Naif (Korelasi)',
            'ATE': naive_res['ATE'],
            'ATE_CI_Lower': boot_ci['naive_ate'][1],
            'ATE_CI_Upper': boot_ci['naive_ate'][2],
            'ATT': naive_res['ATT'],
            'ATT_CI_Lower': boot_ci['naive_ate'][1],
            'ATT_CI_Upper': boot_ci['naive_ate'][2],
            'Keterangan': 'Mengabaikan bias seleksi'
        },
        {
            'Metode': 'Propensity Score Matching (PSM)',
            'ATE': np.nan,
            'ATE_CI_Lower': np.nan,
            'ATE_CI_Upper': np.nan,
            'ATT': psm_att,
            'ATT_CI_Lower': boot_ci['psm_att'][1],
            'ATT_CI_Upper': boot_ci['psm_att'][2],
            'Keterangan': 'ATT diukur via pencocokan 1:1'
        },
        {
            'Metode': 'Inverse Probability Weighting (IPW)',
            'ATE': ipw_ate,
            'ATE_CI_Lower': boot_ci['ipw_ate'][1],
            'ATE_CI_Upper': boot_ci['ipw_ate'][2],
            'ATT': ipw_att,
            'ATT_CI_Lower': boot_ci['ipw_att'][1],
            'ATT_CI_Upper': boot_ci['ipw_att'][2],
            'Keterangan': 'Pembobotan peluang terbalik'
        },
        {
            'Metode': 'Doubly Robust (AIPW)',
            'ATE': dr_ate,
            'ATE_CI_Lower': boot_ci['dr_ate'][1],
            'ATE_CI_Upper': boot_ci['dr_ate'][2],
            'ATT': dr_att,
            'ATT_CI_Lower': boot_ci['dr_att'][1],
            'ATT_CI_Upper': boot_ci['dr_att'][2],
            'Keterangan': 'Kombinasi model treatment & outcome'
        }
    ]
    
    summary_df = pd.DataFrame(summary_data)
    print("\n=== RINGKASAN ESTIMASI EFEK KAUSAL DENGAN BOOTSTRAP 95% CI ===")
    print(summary_df[['Metode', 'ATE', 'ATT', 'Keterangan']].to_string(index=False))
    
    # Save summary to csv
    summary_df.to_csv(os.path.join(PROJECT_ROOT, "data", "processed", "causal_estimates_summary.csv"), index=False)
    
    return summary_df, df, matched_df

if __name__ == "__main__":
    run_all_estimators()
