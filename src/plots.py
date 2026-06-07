import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set project root path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set aesthetic style
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Liberation Sans', 'DejaVu Sans'],
    'figure.titlesize': 16,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 11
})

# Curated premium color palette
PALETTE = {
    'control': '#34495e',     # Sleek Dark Slate
    'treatment': '#e74c3c',   # Vibrant Coral/Red
    'neutral_blue': '#2980b9',# Muted Blue
    'grid': '#ecf0f1'
}

def plot_treatment_distribution(df, output_path=None):
    """
    Plots the distribution of patients receiving RHC vs No RHC.
    """
    if output_path is None:
        output_path = os.path.join(PROJECT_ROOT, "reports", "figures", "01_treatment_distribution.png")
    plt.figure(figsize=(7, 5))
    ax = sns.countplot(
        x='treatment',
        data=df,
        palette=[PALETTE['control'], PALETTE['treatment']],
        hue='treatment',
        legend=False
    )
    
    # Customize labels
    plt.title("Distribusi Pasien: RHC vs Kontrol (No RHC)", pad=15)
    plt.xlabel("Status Intervensi (Treatment)")
    plt.ylabel("Jumlah Pasien")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Kontrol (No RHC)", "Treatment (RHC)"])
    
    # Add counts on top of bars
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}\n({p.get_height()/len(df)*100:.1f}%)', 
                    (p.get_x() + p.get_width() / 2., p.get_height() - 250),
                    ha='center', va='center', color='white', fontweight='bold', fontsize=11)
        
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Treatment distribution plot saved to {output_path}")

def plot_outcome_by_treatment(df, output_path=None):
    """
    Plots the 30-day mortality rate by treatment group (naive correlation).
    """
    if output_path is None:
        output_path = os.path.join(PROJECT_ROOT, "reports", "figures", "02_outcome_by_treatment.png")
    # Calculate mortality rates
    summary = df.groupby('treatment')['outcome'].mean().reset_index()
    summary['mortality_pct'] = summary['outcome'] * 100
    
    plt.figure(figsize=(7, 5))
    ax = sns.barplot(
        x='treatment',
        y='mortality_pct',
        data=summary,
        palette=[PALETTE['control'], PALETTE['treatment']],
        hue='treatment',
        legend=False
    )
    
    plt.title("Tingkat Mortalitas 30 Hari: Naif vs Kausal", pad=15)
    plt.xlabel("Status Intervensi (Treatment)")
    plt.ylabel("Tingkat Mortalitas (%)")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Kontrol (No RHC)", "Treatment (RHC)"])
    ax.set_ylim(0, 100)
    
    # Add values on top of bars
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.2f}%', 
                    (p.get_x() + p.get_width() / 2., p.get_height() + 2),
                    ha='center', va='bottom', color='black', fontweight='bold', fontsize=11)
        
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Outcome by treatment plot saved to {output_path}")

def calculate_smd(df, covariates, treatment_col='treatment'):
    """
    Calculates the Standardized Mean Difference (SMD) for numerical/binary covariates.
    SMD = (Mean(T=1) - Mean(T=0)) / sqrt((Var(T=1) + Var(T=0)) / 2)
    """
    smds = []
    
    treatment_df = df[df[treatment_col] == 1]
    control_df = df[df[treatment_col] == 0]
    
    for cov in covariates:
        # Check if the column exists
        if cov not in df.columns:
            continue
            
        # Skip string/object columns for manual calculation, we should dummy encode them first
        if not np.issubdtype(df[cov].dtype, np.number) and not df[cov].dtype == bool:
            continue
            
        mean_t = treatment_df[cov].mean()
        mean_c = control_df[cov].mean()
        
        var_t = treatment_df[cov].var()
        var_c = control_df[cov].var()
        
        pooled_sd = np.sqrt((var_t + var_c) / 2)
        
        if pooled_sd == 0:
            smd = 0
        else:
            smd = (mean_t - mean_c) / pooled_sd
            
        smds.append({
            'covariate': cov,
            'smd': smd
        })
        
    return pd.DataFrame(smds)

def plot_love_plot(smd_df, output_path=None, title="Love Plot: Keseimbangan Kovariat Awal (Belum Disesuaikan)"):
    """
    Generates a Love Plot of Standardized Mean Differences (SMDs).
    A threshold of |SMD| < 0.1 is standard to indicate good balance.
    """
    if output_path is None:
        output_path = os.path.join(PROJECT_ROOT, "reports", "figures", "03_love_plot_unadjusted.png")
    # Sort by absolute SMD for better readability
    smd_df['abs_smd'] = smd_df['smd'].abs()
    smd_df = smd_df.sort_values(by='abs_smd', ascending=True)
    
    # We might have too many covariates, let's select top 30 most imbalanced or show all if short.
    # RHC has many covariates, so let's display the top 35 or those with absolute SMD > 0.05
    if len(smd_df) > 35:
        # Keep top 15 most imbalanced and 10 most balanced for display, or just top 35 largest absolute SMD
        smd_df_plot = smd_df.tail(35)
    else:
        smd_df_plot = smd_df
        
    plt.figure(figsize=(10, 10))
    
    # Plot the dots
    plt.scatter(smd_df_plot['smd'], range(len(smd_df_plot)), color=PALETTE['neutral_blue'], zorder=3, s=60, label="Unadjusted")
    
    # Add y-ticks
    plt.yticks(range(len(smd_df_plot)), smd_df_plot['covariate'])
    
    # Add vertical lines at -0.1 and 0.1 (standard thresholds)
    plt.axvline(x=0.0, color='gray', linestyle='-', linewidth=1)
    plt.axvline(x=0.1, color='red', linestyle='--', linewidth=1.2, label='Threshold |SMD| = 0.1')
    plt.axvline(x=-0.1, color='red', linestyle='--', linewidth=1.2)
    
    # Add shading for the balanced zone
    plt.axvspan(-0.1, 0.1, color='green', alpha=0.08)
    
    plt.title(title, pad=15)
    plt.xlabel("Standardized Mean Difference (SMD)")
    plt.ylabel("Kovariat (Confounders)")
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Love plot saved to {output_path}")
