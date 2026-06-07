import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from dag import get_confounders, init_dowhy_model, identify_causal_effect

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def estimate_propensity_scores(df):
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
    print(f"Propensity scores estimated. Range: [{df['propensity_score'].min():.4f}, {df['propensity_score'].max():.4f}]")
    return df

def estimate_naive_effect(df):
    """
    Computes the naive risk difference (difference in mortality rates).
    """
    p_treat = df[df['treatment'] == 1]['outcome'].mean()
    p_control = df[df['treatment'] == 0]['outcome'].mean()
    
    naive_ate = p_treat - p_control
    print(f"Naive ATE (Risk Difference): {naive_ate:+.4f} (RHC: {p_treat:.4f}, No RHC: {p_control:.4f})")
    return {
        'method': 'Naive (Korelasi)',
        'ATE': naive_ate,
        'ATT': naive_ate  # For naive, they are the same
    }

def estimate_effect_psm(df, caliper=0.2):
    """
    Performs 1:1 Propensity Score Matching without replacement.
    Estimates ATT (Average Treatment Effect on the Treated).
    """
    # Split into treated and control
    treated = df[df['treatment'] == 1].copy()
    control = df[df['treatment'] == 0].copy()
    
    # Convert propensity scores to log-odds (logit) for better matching metrics
    def logit(p):
        return np.log(p / (1 - p))
        
    treated['ps_logit'] = logit(treated['propensity_score'])
    control['ps_logit'] = logit(control['propensity_score'])
    
    # Calculate caliper width based on standard deviation of logit of PS in treated group
    caliper_width = caliper * treated['ps_logit'].std()
    
    # Match using NearestNeighbors
    nn = NearestNeighbors(n_neighbors=1, metric='manhattan')
    nn.fit(control['ps_logit'].values.reshape(-1, 1))
    
    distances, indices = nn.kneighbors(treated['ps_logit'].values.reshape(-1, 1))
    
    # Filter matches within the caliper
    matched_control_indices = []
    valid_treated_indices = []
    
    for i in range(len(treated)):
        if distances[i][0] <= caliper_width:
            # indices[i][0] gives index in the 'control' dataframe
            matched_control_indices.append(control.index[indices[i][0]])
            valid_treated_indices.append(treated.index[i])
            
    # Create matched datasets
    matched_treated_df = df.loc[valid_treated_indices]
    matched_control_df = df.loc[matched_control_indices]
    
    # Estimate ATT
    att = matched_treated_df['outcome'].mean() - matched_control_df['outcome'].mean()
    print(f"PSM matched: {len(valid_treated_indices)} out of {len(treated)} treated patients ({len(valid_treated_indices)/len(treated)*100:.1f}%)")
    print(f"PSM ATT: {att:+.4f} (Matched RHC: {matched_treated_df['outcome'].mean():.4f}, Matched Control: {matched_control_df['outcome'].mean():.4f})")
    
    # Prepare matched dataframe for balance evaluation
    matched_df = pd.concat([matched_treated_df, matched_control_df])
    
    return att, matched_df

def estimate_effect_ipw(df):
    """
    Estimates ATE and ATT using Inverse Probability Weighting (IPW) with stabilized weights.
    """
    ps = df['propensity_score'].values
    T = df['treatment'].values
    Y = df['outcome'].values
    
    p_t = T.mean() # Overall probability of treatment
    
    # Stabilized ATE weights
    # w_ate = T * (p_t / ps) + (1 - T) * ((1 - p_t) / (1 - ps))
    w_ate = T / ps + (1 - T) / (1 - ps)
    
    # ATT weights
    w_att = T + (ps * (1 - T)) / (1 - ps)
    
    # Weighted outcomes
    ate = np.sum((T * Y) / ps) / np.sum(T / ps) - np.sum(((1 - T) * Y) / (1 - ps)) / np.sum((1 - T) / (1 - ps))
    
    # Standard weighted average ATT
    att = np.sum(T * Y) / np.sum(T) - np.sum((ps * (1 - T) * Y) / (1 - ps)) / np.sum((ps * (1 - T)) / (1 - ps))
    
    print(f"IPW ATE: {ate:+.4f}")
    print(f"IPW ATT: {att:+.4f}")
    
    return ate, att, w_ate, w_att

def estimate_effect_doubly_robust(df):
    """
    Estimates ATE and ATT using Doubly Robust (AIPW) Estimation.
    Uses LogisticRegression for both propensity score and outcome models (since outcome is binary).
    """
    confounders = get_confounders(df)
    X = df[confounders]
    T = df['treatment'].values
    Y = df['outcome'].values
    ps = df['propensity_score'].values
    
    # Train outcome models for treated (T=1) and control (T=0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model_y1 = LogisticRegression(max_iter=2000, random_state=42)
    model_y1.fit(X_scaled[T == 1], Y[T == 1])
    
    model_y0 = LogisticRegression(max_iter=2000, random_state=42)
    model_y0.fit(X_scaled[T == 0], Y[T == 0])
    
    # Predict potential outcomes for all subjects
    mu_1 = model_y1.predict_proba(X_scaled)[:, 1]
    mu_0 = model_y0.predict_proba(X_scaled)[:, 1]
    
    # DR ATE calculation
    dr_ate = np.mean(
        (mu_1 + (T * (Y - mu_1)) / ps) - 
        (mu_0 + ((1 - T) * (Y - mu_0)) / (1 - ps))
    )
    
    # DR ATT calculation
    # DR_ATT = 1/N_T * sum [ T * Y - ( T * mu_0 + (ps * (1 - T) * (Y - mu_0)) / (1 - ps) ) ]
    n_t = np.sum(T)
    dr_att = np.sum(
        T * Y - (T * mu_0 + (ps * (1 - T) * (Y - mu_0)) / (1 - ps))
    ) / n_t
    
    print(f"Doubly Robust ATE: {dr_ate:+.4f}")
    print(f"Doubly Robust ATT: {dr_att:+.4f}")
    
    return dr_ate, dr_att

def run_all_estimators():
    """
    Loads data, runs all estimators, and prints a comparative summary.
    """
    encoded_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_encoded.csv")
    if not os.path.exists(encoded_path):
        raise FileNotFoundError(f"Encoded dataset not found at {encoded_path}. Run eda.py first.")
        
    df = pd.read_csv(encoded_path)
    
    # 1. Estimate Propensity Scores
    df = estimate_propensity_scores(df)
    
    # 2. Naive Estimate
    naive_res = estimate_naive_effect(df)
    
    # 3. PSM Estimate
    psm_att, matched_df = estimate_effect_psm(df)
    
    # 4. IPW Estimate
    ipw_ate, ipw_att, w_ate, w_att = estimate_effect_ipw(df)
    
    # 5. Doubly Robust Estimate
    dr_ate, dr_att = estimate_effect_doubly_robust(df)
    
    # Save the matched and weighted dataset
    df['weights_ate'] = w_ate
    df['weights_att'] = w_att
    df.to_csv(os.path.join(PROJECT_ROOT, "data", "processed", "rhc_estimated.csv"), index=False)
    matched_df.to_csv(os.path.join(PROJECT_ROOT, "data", "processed", "rhc_matched.csv"), index=False)
    print("Matched and weighted datasets saved.")
    
    # Create summary DataFrame
    summary_df = pd.DataFrame([
        {'Metode': 'Naif (Korelasi)', 'ATE': naive_res['ATE'], 'ATT': naive_res['ATT'], 'Keterangan': 'Mengabaikan bias seleksi'},
        {'Metode': 'Propensity Score Matching (PSM)', 'ATE': np.nan, 'ATT': psm_att, 'Keterangan': 'ATT diukur via pencocokan 1:1'},
        {'Metode': 'Inverse Probability Weighting (IPW)', 'ATE': ipw_ate, 'ATT': ipw_att, 'Keterangan': 'Pembobotan peluang terbalik'},
        {'Metode': 'Doubly Robust (AIPW)', 'ATE': dr_ate, 'ATT': dr_att, 'Keterangan': 'Kombinasi model treatment & outcome'}
    ])
    
    print("\n=== RINGKASAN ESTIMASI EFEK KAUSAL ===")
    print(summary_df.to_string(index=False))
    return summary_df, df, matched_df

if __name__ == "__main__":
    run_all_estimators()
