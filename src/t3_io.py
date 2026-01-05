"""
BrAPI client utilities for interacting with T3/Wheat.
"""

import requests
import pandas as pd

T3_BASE = "https://wheat.triticeaetoolbox.org/brapi/v2"


# -----------------------------
# Core GET helper with pagination
# -----------------------------
def brapi_get(endpoint, params=None):
    url = f"{T3_BASE}/{endpoint}"
    params = params or {}

    all_data = []
    page = 0

    while True:
        params.update({"page": page})
        r = requests.get(url, params=params)
        r.raise_for_status()
        j = r.json()

        data = j.get("result", {}).get("data", [])
        all_data.extend(data)

        pagination = j.get("metadata", {}).get("pagination", {})
        if page >= pagination.get("totalPages", 0) - 1:
            break

        page += 1

    return all_data


# -----------------------------
# Germplasm
# -----------------------------
def get_germplasm_by_name(names):
    if isinstance(names, str):
        names = [names]

    dfs = []
    for n in names:
        data = brapi_get("germplasm", params={"germplasmName": n})
        if data:
            dfs.append(pd.DataFrame(data))

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


# -----------------------------
# Studies
# -----------------------------
def get_study_metadata(study_dbid):
    return brapi_get(f"studies/{study_dbid}")


def search_studies_by_name(name):
    data = brapi_get("studies-search", params={"studyName": name})
    return pd.DataFrame(data)


# -----------------------------
# Genotyping Protocols
# -----------------------------
def get_genotyping_protocols():
    data = brapi_get("geno/protocols")
    return pd.DataFrame(data)


def choose_best_protocol():
    """
    Choose a genotyping protocol from T3/Wheat.
    Strategy: pick the protocol with the most markers.
    """
    df = get_genotyping_protocols()

    if df.empty:
        raise RuntimeError("No genotyping protocols returned by T3.")

    # Look for a marker count column
    marker_cols = [c for c in df.columns if "marker" in c.lower()]

    if marker_cols:
        best = df.sort_values(marker_cols[0], ascending=False).iloc[0]
    else:
        # fallback: just pick the first protocol
        best = df.iloc[0]

    return best


# -----------------------------
# Genotype Matrix
# -----------------------------
def get_genotype_matrix(protocol_dbid, germplasm_ids=None):
    params = {}
    if germplasm_ids:
        params["germplasmDbIds"] = ",".join(germplasm_ids)

    data = brapi_get(f"geno/protocols/{protocol_dbid}/calls", params=params)
    return pd.DataFrame(data)


# -----------------------------
# Phenotype Observations
# -----------------------------
def get_observations(study_dbid):
    data = brapi_get("observations", params={"studyDbId": study_dbid})
    return pd.DataFrame(data)
