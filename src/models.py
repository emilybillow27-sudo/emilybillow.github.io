# src/models.py

import pandas as pd
import numpy as np
from grm import build_grm

def fit_model(train_pheno: pd.DataFrame, geno: pd.DataFrame, env: pd.DataFrame):
    """
    Fit the multi-environment genomic prediction model.
    This is a placeholder for:
      - GBLUP-GxE
      - ML ensemble
    """
    # TODO: build design matrices
    # TODO: compute GRM
    # TODO: solve mixed model or ridge regression
    model = {"placeholder": True}
    return model

def predict_for_trial(model, focal_trial, test_accessions, geno, env):
    """
    Generate predictions for all genotyped accessions in the focal trial.
    """
    # TODO: extract genotype rows
    # TODO: compute predictions
    preds = pd.DataFrame({
        "germplasmName": test_accessions,
        "prediction": np.zeros(len(test_accessions))  # placeholder
    })
    return preds
