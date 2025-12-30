"""
cv_protocols.py

Implements CV0 and CV00 dataset construction for the T3/Wheat Predictathon.
Uses env_id and accession identifiers to partition phenotypes and genotypes.

Author: Emily Billow
"""

import pandas as pd
from typing import Dict, Tuple


def build_cv0(pheno: pd.DataFrame, geno: pd.DataFrame, focal_env: str) -> Dict[str, pd.DataFrame]:
    """
    CV0: Exclude the focal trial (environment) from training.
    Train on all other environments; predict on focal_env.

    Returns:
        {
            "train_pheno": DataFrame,
            "test_pheno": DataFrame,
            "train_geno": DataFrame,
            "test_geno": DataFrame
        }
    """
    train_pheno = pheno[pheno["env_id"] != focal_env]
    test_pheno = pheno[pheno["env_id"] == focal_env]

    # Accessions in each set
    train_acc = set(train_pheno["germplasmName"])
    test_acc = set(test_pheno["germplasmName"])

    train_geno = geno[geno["germplasmName"].isin(train_acc)]
    test_geno = geno[geno["germplasmName"].isin(test_acc)]

    return {
        "train_pheno": train_pheno,
        "test_pheno": test_pheno,
        "train_geno": train_geno,
        "test_geno": test_geno,
    }


def build_cv00(pheno: pd.DataFrame, geno: pd.DataFrame, focal_env: str) -> Dict[str, pd.DataFrame]:
    """
    CV00: Exclude the focal trial AND all accessions that appear in that trial.
    This is the strictest form of generalization.

    Returns:
        {
            "train_pheno": DataFrame,
            "test_pheno": DataFrame,
            "train_geno": DataFrame,
            "test_geno": DataFrame
        }
    """
    # Accessions appearing in focal environment
    focal_acc = set(pheno.loc[pheno["env_id"] == focal_env, "germplasmName"])

    # Training phenotypes exclude:
    #   - the focal environment
    #   - any accession that appears in the focal environment
    train_pheno = pheno[
        (pheno["env_id"] != focal_env) &
        (~pheno["germplasmName"].isin(focal_acc))
    ]

    test_pheno = pheno[pheno["env_id"] == focal_env]

    train_acc = set(train_pheno["germplasmName"])
    test_acc = set(test_pheno["germplasmName"])

    train_geno = geno[geno["germplasmName"].isin(train_acc)]
    test_geno = geno[geno["germplasmName"].isin(test_acc)]

    return {
        "train_pheno": train_pheno,
        "test_pheno": test_pheno,
        "train_geno": train_geno,
        "test_geno": test_geno,
    }
