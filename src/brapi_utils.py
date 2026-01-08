# src/brapi_utils.py

import pandas as pd

def fetch_trait_metadata():
    """
    Minimal placeholder BrAPI metadata fetcher.
    Returns an empty DataFrame with expected columns.
    Replace with real BrAPI calls when ready.
    """
    return pd.DataFrame(columns=[
        "observationVariableDbId",
        "traitName",
        "traitDescription",
        "methodName",
        "scaleName"
    ])
