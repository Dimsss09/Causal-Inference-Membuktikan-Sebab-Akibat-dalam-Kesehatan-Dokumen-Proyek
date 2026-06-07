import os
import pandas as pd
import numpy as np
from dowhy import CausalModel

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_confounders(df):
    """
    Returns the list of confounders from the encoded dataframe.
    Excludes identifiers, treatment, outcome, and raw categorical variables.
    """
    exclude = [
        'treatment', 'outcome', 'Unnamed: 0', 'ptid', 'death', 'swang1', 
        'dth30', 'sadmdte', 'dschdte', 'dthdte', 'lstctdte',
        'cat1', 'sex', 'race', 'income', 'ninsclas', 'dnr1', 'ca', 'cat2',
        'adld3p', 'urin1'
    ]
    return [col for col in df.columns if col not in exclude]

def build_gml_graph(treatment, outcome, confounders):
    """
    Programmatically builds a Directed Acyclic Graph (DAG) in GML format.
    - All confounders point to both treatment and outcome.
    - Treatment points to outcome.
    """
    gml = "graph [\n    directed 1\n"
    gml += f'    node [ id "{treatment}" label "{treatment}" ]\n'
    gml += f'    node [ id "{outcome}" label "{outcome}" ]\n'
    
    # Add nodes for confounders
    for c in confounders:
        # Avoid issues with spaces or special characters in GML ids
        # (Though we clean column names or use dummy columns which have underscores)
        gml += f'    node [ id "{c}" label "{c}" ]\n'
        
    # Add edges: Confounders -> Treatment and Confounders -> Outcome
    for c in confounders:
        gml += f'    edge [ source "{c}" target "{treatment}" ]\n'
        gml += f'    edge [ source "{c}" target "{outcome}" ]\n'
        
    # Add treatment -> outcome edge
    gml += f'    edge [ source "{treatment}" target "{outcome}" ]\n'
    gml += "]"
    return gml

def init_dowhy_model(df, treatment='treatment', outcome='outcome'):
    """
    Initializes a DoWhy CausalModel with the dataset and programmatically generated DAG.
    """
    confounders = get_confounders(df)
    gml_graph = build_gml_graph(treatment, outcome, confounders)
    
    print(f"Initializing DoWhy CausalModel with {len(confounders)} confounders...")
    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        graph=gml_graph
    )
    return model

def identify_causal_effect(model):
    """
    Identifies the causal effect using backdoor criterion.
    """
    print("Identifying causal effect...")
    identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
    print("Causal effect identified successfully!")
    return identified_estimand

if __name__ == "__main__":
    encoded_path = os.path.join(PROJECT_ROOT, "data", "processed", "rhc_encoded.csv")
    if not os.path.exists(encoded_path):
        raise FileNotFoundError(f"Encoded dataset not found at {encoded_path}. Run eda.py first.")
        
    df = pd.read_csv(encoded_path)
    model = init_dowhy_model(df)
    estimand = identify_causal_effect(model)
    print("\n--- Identified Estimand ---")
    try:
        print(estimand)
    except UnicodeEncodeError:
        print(str(estimand).encode('ascii', errors='replace').decode('ascii'))
