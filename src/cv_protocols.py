# src/cv_protocols.py

import pandas as pd

def build_cv_datasets(pheno: pd.DataFrame, focal_trial: str, cv_type: str):
    """Return training phenotypes, training trials, training accessions, test accessions."""

    focal_pheno = pheno[pheno["studyName"] == focal_trial]
    focal_accessions = set(focal_pheno["germplasmName"])

    # Test set = genotyped accessions in focal trial
    test_accessions = sorted(focal_accessions)

    if cv_type == "CV0":
        train_pheno = pheno[pheno["studyName"] != focal_trial]

    elif cv_type == "CV00":
        train_pheno = pheno[
            (pheno["studyName"] != focal_trial) &
            (~pheno["germplasmName"].isin(focal_accessions))
        ]

    train_trials = sorted(train_pheno["studyName"].unique())
    train_accessions = sorted(train_pheno["germplasmName"].unique())

    return train_pheno, train_trials, train_accessions, test_accessions
