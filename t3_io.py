# src/t3_io.py

import pandas as pd

def load_raw_phenotypes(path: str) -> pd.DataFrame:
    """Load raw phenotype CSV downloaded from T3."""
    return pd.read_csv(path)

def load_raw_genotypes(path: str) -> pd.DataFrame:
    """Load raw genotype CSV or TSV."""
    return pd.read_csv(path)

def load_trial_metadata(path: str) -> pd.DataFrame:
    """Load trial metadata."""
    return pd.read_csv(path)

# Optional: BrAPI access functions
def fetch_from_brapi(endpoint: str, params: dict):
    """Template for BrAPI GET requests."""
    raise NotImplementedError
