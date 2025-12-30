# src/t3_io.py

import pandas as pd
import requests


# ---------------------------------------------------------
# 1. File Loading Helpers
# ---------------------------------------------------------

def load_raw_phenotypes(path: str) -> pd.DataFrame:
    """
    Load raw phenotype CSV/TSV downloaded from T3.
    Automatically detects delimiter and normalizes column names.
    """
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = df.columns.str.strip()
    return df


def load_raw_genotypes(path: str) -> pd.DataFrame:
    """
    Load raw genotype CSV/TSV.
    Automatically detects delimiter and normalizes column names.
    """
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = df.columns.str.strip()
    return df


def load_trial_metadata(path: str) -> pd.DataFrame:
    """
    Load trial metadata CSV/TSV.
    """
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = df.columns.str.strip()
    return df


# ---------------------------------------------------------
# 2. Optional BrAPI Access
# ---------------------------------------------------------

def fetch_from_brapi(base_url: str, endpoint: str, params: dict = None) -> pd.DataFrame:
    """
    Fetch data from a BrAPI endpoint and return as a DataFrame.

    Args:
        base_url: e.g., "https://wheat.triticeaetoolbox.org/brapi/v2"
        endpoint: e.g., "phenotypes", "germplasm", "trials"
        params: dict of query parameters

    Returns:
        DataFrame containing the BrAPI response data.
    """
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    response = requests.get(url, params=params or {})

    if response.status_code != 200:
        raise RuntimeError(f"BrAPI request failed: {response.status_code} — {response.text}")

    data = response.json()

    # BrAPI responses usually store data in "result" or "result.data"
    if "result" in data:
        if isinstance(data["result"], dict) and "data" in data["result"]:
            return pd.DataFrame(data["result"]["data"])
        return pd.DataFrame(data["result"])

    if "data" in data:
        return pd.DataFrame(data["data"])

    raise ValueError("Unexpected BrAPI response format.")
