# src/phenotype_utils.py

import pandas as pd

def harmonize_trait_names(pheno_df, vars_df):
    """Replace long trait names with abbreviations when available."""
    mapping = dict(
        zip(vars_df["observationVariableDbId"], vars_df["abbreviation"])
    )

    # Replace variableDbId → abbreviation
    if "observationVariableDbId" in pheno_df.columns:
        pheno_df["trait"] = pheno_df["observationVariableDbId"].map(mapping).fillna(
            pheno_df.get("trait", pheno_df.get("name"))
        )

    return pheno_df

def extract_environment_covariates(meta_df):
    """Extract environment-level covariates from trial metadata."""
    keep = [
        "studyDbId",
        "location",
        "year",
        "designType",
        "plantingDate",
        "harvestDate",
        "plotWidth",
        "plotLength",
        "fieldSize",
    ]
    return meta_df[keep]
