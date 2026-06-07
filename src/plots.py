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

def plot_dag(output_path=None):
    """
    Plots a clean, simplified causal Directed Acyclic Graph (DAG).
    """
    if output_path is None:
        output_path = os.path.join(PROJECT_ROOT, "reports", "figures", "04_causal_dag.png")
        
    import networkx as nx
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes with custom labels
    nodes = {
        'X': "Confounders\n(APACHE, Usia,\nKomorbiditas, dll)",
        'T': "Treatment\n(RHC)",
        'Y': "Outcome\n(Mortalitas 30 Hari)",
        'M': "Mediator\n(Perubahan\nTatalaksana)"
    }
    
    for k, v in nodes.items():
        G.add_node(k, label=v)
        
    # Add edges
    edges = [
        ('X', 'T'),
        ('X', 'Y'),
        ('T', 'Y'),
        ('T', 'M'),
        ('M', 'Y')
    ]
    G.add_edges_from(edges)
    
    # Define custom positions for layout (Left-to-Right + hierarchical)
    pos = {
        'X': (0.5, 0.8),  # Confounders at the top center
        'T': (0.15, 0.2), # Treatment bottom-left
        'M': (0.5, 0.2),  # Mediator bottom-middle
        'Y': (0.85, 0.2)  # Outcome bottom-right
    }
    
    plt.figure(figsize=(9, 6))
    
    # Draw nodes
    # Confounder (X) - Slate Gray
    nx.draw_networkx_nodes(G, pos, nodelist=['X'], node_color='#7f8c8d', node_size=3500, alpha=0.95, edgecolors='black', linewidths=1.5)
    # Treatment (T) - Red/Coral
    nx.draw_networkx_nodes(G, pos, nodelist=['T'], node_color=PALETTE['treatment'], node_size=3500, alpha=0.95, edgecolors='black', linewidths=1.5)
    # Outcome (Y) - Blue/Slate
    nx.draw_networkx_nodes(G, pos, nodelist=['Y'], node_color=PALETTE['control'], node_size=3500, alpha=0.95, edgecolors='black', linewidths=1.5)
    # Mediator (M) - Muted Blue
    nx.draw_networkx_nodes(G, pos, nodelist=['M'], node_color=PALETTE['neutral_blue'], node_size=3500, alpha=0.9, edgecolors='black', linewidths=1.5, node_shape='s')
    
    # Draw edges with arrows
    nx.draw_networkx_edges(
        G, pos, 
        edgelist=edges, 
        width=2, 
        arrowstyle='-|>', 
        arrowsize=25, 
        edge_color='#2c3e50',
        connectionstyle='arc3,rad=0.02'
    )
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, labels=nodes, font_size=8, font_family='sans-serif', font_color='white', font_weight='bold')
    
    # Backdoor path text annotation
    plt.text(0.32, 0.55, "Jalur Belakang (Backdoor): T <-- X --> Y\n(Bias Indikasi, harus disesuaikan)", fontsize=9, color='#c0392b', fontweight='bold', ha='center')
    plt.text(0.5, 0.05, "Jalur Kausal Efek Total (T --> Y dan T --> M --> Y)", fontsize=9, color='#27ae60', fontweight='bold', ha='center')
    
    plt.title("Causal DAG: Pemasangan RHC & Mortalitas ICU", pad=20, fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"DAG plot saved to {output_path}")

def plot_propensity_score_distribution(df, ps_col='propensity_score', output_path=None):
    """
    Plots the distribution of propensity scores for treatment vs control (overlap evaluation).
    """
    if output_path is None:
        output_path = os.path.join(PROJECT_ROOT, "reports", "figures", "05_propensity_score_overlap.png")
        
    plt.figure(figsize=(8, 5))
    sns.kdeplot(
        data=df[df['treatment'] == 0],
        x=ps_col,
        fill=True,
        color=PALETTE['control'],
        label='Kontrol (No RHC)',
        alpha=0.4,
        linewidth=2
    )
    sns.kdeplot(
        data=df[df['treatment'] == 1],
        x=ps_col,
        fill=True,
        color=PALETTE['treatment'],
        label='Treatment (RHC)',
        alpha=0.4,
        linewidth=2
    )
    
    plt.title("Distribusi Propensity Score: Evaluasi Asumsi Overlap (Positivity)", pad=15, fontsize=12, fontweight='bold')
    plt.xlabel("Propensity Score (P(RHC | X))")
    plt.ylabel("Kepadatan (Density)")
    plt.xlim(0, 1)
    plt.legend(loc="upper right")
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Propensity score overlap plot saved to {output_path}")

def plot_love_plot_comparison(unadjusted_smd_df, adjusted_smd_df, method_label="Matched/Weighted", output_path=None):
    """
    Generates a Love Plot comparing SMDs before vs after adjustment.
    """
    if output_path is None:
        output_path = os.path.join(PROJECT_ROOT, "reports", "figures", "06_love_plot_comparison.png")
        
    merged = pd.merge(
        unadjusted_smd_df[['covariate', 'smd']], 
        adjusted_smd_df[['covariate', 'smd']], 
        on='covariate', 
        suffixes=('_unadj', '_adj')
    )
    
    merged['abs_unadj'] = merged['smd_unadj'].abs()
    merged = merged.sort_values(by='abs_unadj', ascending=True)
    
    if len(merged) > 30:
        merged_plot = merged.tail(30)
    else:
        merged_plot = merged
        
    plt.figure(figsize=(10, 9))
    
    # Plot unadjusted (Slate Gray)
    plt.scatter(
        merged_plot['smd_unadj'], 
        range(len(merged_plot)), 
        color='#7f8c8d', 
        zorder=3, 
        s=60, 
        label="Sebelum Penyesuaian (Unadjusted)",
        alpha=0.7
    )
    
    # Plot adjusted (Green)
    plt.scatter(
        merged_plot['smd_adj'], 
        range(len(merged_plot)), 
        color='#27ae60', 
        zorder=4, 
        s=60, 
        label=f"Sesudah Penyesuaian ({method_label})",
        marker='D'
    )
    
    # Connect dots
    for i in range(len(merged_plot)):
        row = merged_plot.iloc[i]
        plt.plot(
            [row['smd_unadj'], row['smd_adj']], 
            [i, i], 
            color='#bdc3c7', 
            linestyle=':', 
            zorder=2
        )
        
    plt.yticks(range(len(merged_plot)), merged_plot['covariate'])
    plt.axvline(x=0.0, color='gray', linestyle='-', linewidth=1)
    plt.axvline(x=0.1, color='red', linestyle='--', linewidth=1.2)
    plt.axvline(x=-0.1, color='red', linestyle='--', linewidth=1.2)
    plt.axvspan(-0.1, 0.1, color='green', alpha=0.08, label='Zona Seimbang (|SMD| < 0.1)')
    
    plt.title("Perbandingan Keseimbangan Kovariat (Covariate Balance)", pad=15, fontsize=13, fontweight='bold')
    plt.xlabel("Standardized Mean Difference (SMD)")
    plt.ylabel("Kovariat (Confounders)")
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Love plot comparison saved to {output_path}")

def plot_effect_comparison(summary_df, output_path=None):
    """
    Plots ATE and ATT estimates with their 95% confidence intervals.
    """
    if output_path is None:
        output_path = os.path.join(PROJECT_ROOT, "reports", "figures", "07_effect_comparison.png")
        
    plt.figure(figsize=(9, 5))
    
    methods = summary_df['Metode'].tolist()
    y_pos = np.arange(len(methods))
    
    ate_vals = summary_df['ATE'].values
    ate_lower = summary_df['ATE_CI_Lower'].values
    ate_upper = summary_df['ATE_CI_Upper'].values
    
    att_vals = summary_df['ATT'].values
    att_lower = summary_df['ATT_CI_Lower'].values
    att_upper = summary_df['ATT_CI_Upper'].values
    
    # Calculate error lengths
    ate_errors = np.zeros((2, len(methods)))
    att_errors = np.zeros((2, len(methods)))
    
    for i in range(len(methods)):
        if not np.isnan(ate_vals[i]) and not np.isnan(ate_lower[i]) and not np.isnan(ate_upper[i]):
            ate_errors[0, i] = ate_vals[i] - ate_lower[i]
            ate_errors[1, i] = ate_upper[i] - ate_vals[i]
            
        if not np.isnan(att_vals[i]) and not np.isnan(att_lower[i]) and not np.isnan(att_upper[i]):
            att_errors[0, i] = att_vals[i] - att_lower[i]
            att_errors[1, i] = att_upper[i] - att_vals[i]
            
    # Plot ATE points and error bars
    plt.errorbar(
        ate_vals, y_pos - 0.15, xerr=ate_errors, fmt='o', color=PALETTE['neutral_blue'],
        elinewidth=2, capsize=5, ms=8, label='ATE (Average Treatment Effect)', alpha=0.9
    )
    
    # Plot ATT points and error bars
    plt.errorbar(
        att_vals, y_pos + 0.15, xerr=att_errors, fmt='D', color=PALETTE['treatment'],
        elinewidth=2, capsize=5, ms=8, label='ATT (Effect on the Treated)', alpha=0.9
    )
    
    # Draw vertical line at 0 (No effect)
    plt.axvline(x=0.0, color='black', linestyle='--', linewidth=1.2, label='No Effect (ATE/ATT = 0)')
    
    plt.yticks(y_pos, methods)
    plt.title("Perbandingan Efek Estimasi RHC Terhadap Mortalitas 30 Hari (95% CI)", pad=15, fontsize=13, fontweight='bold')
    plt.xlabel("Estimasi Efek (Risk Difference)")
    plt.ylabel("Metode Analisis")
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.xlim(-0.02, 0.10)
    
    # Add percentage label to x-axis
    import matplotlib.ticker as mtick
    plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Causal effect comparison plot saved to {output_path}")
