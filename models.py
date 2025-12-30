"""
models.py

Implements baseline GBLUP, optional G×E modeling, and an ML ensemble hook.
Designed for use with preprocessed phenotype, genotype, and GRM matrices.

Author: Emily Billow
"""

import numpy as np
import pandas as pd
from typing import Dict


# ---------------------------------------------------------------------
# 1. Baseline GBLUP
# ---------------------------------------------------------------------

def gblup_predict(train_pheno: pd.DataFrame,
                  train_geno: pd.DataFrame,
                  test_geno: pd.DataFrame,
                  G: np.ndarray,
                  trait_col: str = "value") -> pd.DataFrame:
    """
    Simple GBLUP: y = μ + g, where g ~ N(0, Gσ²)

    Args:
        train_pheno: phenotype DataFrame with germplasmName + trait value
        train_geno: genotype DataFrame aligned to GRM rows
        test_geno: genotype DataFrame aligned to GRM rows
        G: genomic relationship matrix (numpy array)
        trait_col: phenotype column to predict

    Returns:
        DataFrame with predictions for test_geno accessions
    """

    # Align GRM rows to training genotypes
    train_ids = list(train_geno["germplasmName"])
    test_ids = list(test_geno["germplasmName"])

    # Indices in GRM
    all_ids = train_ids + test_ids
    idx = {g: i for i, g in enumerate(all_ids)}

    # Subset GRM
    G_train = G[np.ix_([idx[g] for g in train_ids], [idx[g] for g in train_ids])]
    G_cross = G[np.ix_([idx[g] for g in test_ids], [idx[g] for g in train_ids])]

    y = train_pheno.set_index("germplasmName").loc[train_ids, trait_col].values

    # Ridge-like solution: g_hat = G (G + λI)^(-1) y
    lam = 1e-5 * np.trace(G_train) / G_train.shape[0]
    A = G_train + lam * np.eye(G_train.shape[0])
    g_hat = G_cross @ np.linalg.solve(A, y)

    return pd.DataFrame({
        "germplasmName": test_ids,
        "GBLUP_pred": g_hat
    })


# ---------------------------------------------------------------------
# 2. Optional ML Ensemble (placeholder)
# ---------------------------------------------------------------------

def ml_ensemble_predict(train_pheno, train_geno, test_geno):
    """
    Placeholder for ML ensemble (e.g., PCA + XGBoost).
    Returns zeros for now.
    """
    return pd.DataFrame({
        "germplasmName": test_geno["germplasmName"],
        "ML_pred": np.zeros(len(test_geno))
    })


# ---------------------------------------------------------------------
# 3. Combined Model
# ---------------------------------------------------------------------

def fit_and_predict(cv_data: Dict[str, pd.DataFrame],
                    G: np.ndarray,
                    trait_col: str = "value",
                    use_ml: bool = False) -> pd.DataFrame:
    """
    Unified interface for CV0/CV00 prediction.

    Args:
        cv_data: dict from cv_protocols.build_cv0 or build_cv00
        G: genomic relationship matrix
        trait_col: phenotype column
        use_ml: whether to include ML ensemble

    Returns:
        DataFrame with predictions
    """

    train_pheno = cv_data["train_pheno"]
    train_geno = cv_data["train_geno"]
    test_geno = cv_data["test_geno"]

    # GBLUP
    gblup_df = gblup_predict(train_pheno, train_geno, test_geno, G, trait_col)

    if not use_ml:
        return gblup_df

    # ML ensemble
    ml_df = ml_ensemble_predict(train_pheno, train_geno, test_geno)

    # Weighted average (placeholder)
    merged = gblup_df.merge(ml_df, on="germplasmName")
    merged["final_pred"] = 0.7 * merged["GBLUP_pred"] + 0.3 * merged["ML_pred"]

    return merged
