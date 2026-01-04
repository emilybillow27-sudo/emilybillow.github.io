# src/models.py

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------
# MODEL DISPATCHER
# ----------------------------------------------------------------------

def fit_model(train_pheno, geno, env, G, model_type="gblup"):
    """
    Dispatch to the requested model type.
    """
    if model_type == "me_gblup":
        return fit_me_gblup(train_pheno, geno, env, G)
    elif model_type == "gblup":
        return fit_gblup(train_pheno, geno, env, G)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")


def predict_for_trial(model, focal_trial, test_accessions, geno, env, G, model_type="gblup"):
    """
    Dispatch prediction to the correct model.
    """
    if model_type == "me_gblup":
        return predict_me_gblup(model, focal_trial, test_accessions, geno, env, G)
    elif model_type == "gblup":
        return predict_gblup(model, focal_trial, test_accessions, geno, env, G)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")
        

# ----------------------------------------------------------------------
# BASELINE GBLUP
# ----------------------------------------------------------------------

def fit_gblup(train_pheno, geno, env, G, lambda_factor=1e-5):
    """
    Baseline GBLUP:
        u_hat = (G + λI)^(-1) y
    """
    from numpy.linalg import inv

    y = train_pheno["value"].values
    accessions = train_pheno["germplasmName"].values

    # Map accessions to rows of G
    geno_ids = geno["germplasmName"].values
    train_idx = [np.where(geno_ids == acc)[0][0] for acc in accessions]

    # Subset G
    G_train = G[np.ix_(train_idx, train_idx)]

    # Regularize
    G_reg = G_train + lambda_factor * np.eye(len(train_idx))

    # Solve
    u_hat = inv(G_reg) @ y

    return {
        "accessions": accessions,
        "u_hat": u_hat,
        "geno_ids": geno_ids,
    }


def predict_gblup(model, focal_trial, test_accessions, geno, env, G):
    """
    Predict breeding values for test accessions using GBLUP.
    """
    geno_ids = model["geno_ids"]

    # Training indices
    train_idx = [np.where(geno_ids == acc)[0][0] for acc in model["accessions"]]

    # Test indices (only those present in geno_ids)
    test_idx = [
        np.where(geno_ids == acc)[0][0]
        for acc in test_accessions
        if acc in geno_ids
    ]

    # Subset G
    G_test_train = G[np.ix_(test_idx, train_idx)]

    # Predict
    y_hat = G_test_train @ model["u_hat"]

    return pd.DataFrame({
        "germplasmName": [geno_ids[i] for i in test_idx],
        "value": y_hat,
        "studyName": focal_trial,
    })


# ----------------------------------------------------------------------
# MULTI‑ENVIRONMENT GBLUP (ME‑GBLUP)
# ----------------------------------------------------------------------

def fit_me_gblup(train_pheno, geno, env, G, h2=0.3):
    """
    Multi‑environment GBLUP:
        y = Xb + Zu
        u ~ N(0, G σ_g^2)
    Environments/trials enter as fixed effects.
    """

    # -----------------------------
    # Align phenotypes
    # -----------------------------
    y = train_pheno["value"].values
    accessions = train_pheno["germplasmName"].values
    trials = train_pheno["studyName"].astype("category")

    # Build accession index
    geno_ids = geno["germplasmName"].values
    train_idx = [np.where(geno_ids == acc)[0][0] for acc in accessions]

    # Subset G
    G_train = G[np.ix_(train_idx, train_idx)]

    # -----------------------------
    # Fixed effects: intercept + trial dummies
    # -----------------------------
    trial_design = pd.get_dummies(trials, drop_first=True)
    X = np.column_stack([
        np.ones(len(train_pheno)),
        trial_design.values,
    ])

    # -----------------------------
    # Estimate fixed effects (OLS approximation)
    # -----------------------------
    XtX = X.T @ X
    Xty = X.T @ y
    beta_hat = np.linalg.solve(XtX + 1e-6 * np.eye(XtX.shape[0]), Xty)

    # Residuals
    y_tilde = y - X @ beta_hat

    # -----------------------------
    # Solve for u_hat
    # -----------------------------
    lam = (1 - h2) / h2
    A = G_train + lam * np.eye(G_train.shape[0])
    alpha = np.linalg.solve(A, y_tilde)
    u_hat = G_train @ alpha

    return {
        "beta_hat": beta_hat,
        "u_hat": u_hat,
        "uniq_acc": accessions,
        "geno_ids": geno_ids,
        "trial_levels": trial_design.columns.tolist(),
        "h2": h2,
    }


def predict_me_gblup(model, focal_trial, test_accessions, geno, env, G):
    """
    Predict phenotypes for test accessions in a focal trial using ME‑GBLUP.
    """

    beta_hat = model["beta_hat"]
    u_hat = model["u_hat"]
    uniq_acc = model["uniq_acc"]
    geno_ids = model["geno_ids"]
    trial_levels = model["trial_levels"]

    # -----------------------------
    # Map test accessions
    # -----------------------------
    test_idx = []
    for acc in test_accessions:
        if acc in uniq_acc:
            # Seen in training
            i = np.where(uniq_acc == acc)[0][0]
            test_idx.append(("seen", i))
        else:
            # Unseen: breeding value = 0
            test_idx.append(("new", None))

    # -----------------------------
    # Build u_test
    # -----------------------------
    u_test = []
    for status, idx in test_idx:
        if status == "seen":
            u_test.append(u_hat[idx])
        else:
            u_test.append(0.0)
    u_test = np.array(u_test)

    # -----------------------------
    # Build fixed‑effect design for focal trial
    # -----------------------------
    trial_row = [0.0] * len(trial_levels)
    if focal_trial in trial_levels:
        j = trial_levels.index(focal_trial)
        trial_row[j] = 1.0

    X_star = np.column_stack([
        np.ones(len(test_accessions)),
        np.tile(trial_row, (len(test_accessions), 1)),
    ])

    # -----------------------------
    # Final prediction
    # -----------------------------
    y_pred = X_star @ beta_hat + u_test

    return pd.DataFrame({
        "germplasmName": test_accessions,
        "value": y_pred,
        "studyName": focal_trial,
    })