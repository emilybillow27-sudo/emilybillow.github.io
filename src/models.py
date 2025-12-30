# src/models.py

import pandas as pd
import numpy as np
from grm import build_grm

def fit_model(train_pheno: pd.DataFrame, geno: pd.DataFrame, env: pd.DataFrame):
    """
    Fit a simple GBLUP model using the GRM.
    """
    from numpy.linalg import inv

    # Extract accessions and trait values
    y = train_pheno["value"].values
    accessions = train_pheno["germplasmName"].values

    # Subset GRM to training accessions
    geno_ids = geno["germplasmName"].values
    train_idx = [np.where(geno_ids == acc)[0][0] for acc in accessions]
    G_full = np.load("data/processed/G_matrix.npz")["G"]
    G_train = G_full[np.ix_(train_idx, train_idx)]

    # Regularize GRM
    lambda_factor = 1e-5
    G_reg = G_train + lambda_factor * np.eye(len(train_idx))

    # Solve GBLUP: u_hat = G_inv @ y
    u_hat = inv(G_reg) @ y

    model = {
        "accessions": accessions,
        "u_hat": u_hat,
        "geno_ids": geno_ids,
        "G_full": G_full
    }
    return model

def predict_for_trial(model, focal_trial, test_accessions, geno, env):
    """
    Predict breeding values for test accessions using fitted GBLUP effects.
    """
    geno_ids = model["geno_ids"]
    G_full = model["G_full"]
    train_idx = [np.where(geno_ids == acc)[0][0] for acc in model["accessions"]]
    test_idx = [np.where(geno_ids == acc)[0][0] for acc in test_accessions if acc in geno_ids]

    # Subset GRM: G_test_train
    G_test_train = G_full[np.ix_(test_idx, train_idx)]

    # Predict: y_hat = G_test_train @ u_hat
    y_hat = G_test_train @ model["u_hat"]

    preds = pd.DataFrame({
        "germplasmName": [geno_ids[i] for i in test_idx],
        "prediction": y_hat
    })
    return preds
