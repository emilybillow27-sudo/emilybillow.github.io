import pandas as pd

# Metadata columns used to identify non-trait fields
METADATA_COLS = [
    "studyName",
    "germplasmName",
    "germplasmDbId",
    "programDbId",
    "programname",
    "programdescription",
    "studydbid",
    "studydescription",
    "studydesign",
    "fieldtrialisplannedtobegenotyped",
    "fieldtrialisplannedtocross",
    "plantingdate",
    "harvestdate",
    "locationdbid",
    "studyYear",
    "locationName",
    "observationlevel",
    "observationunitdbid",
    "observationunitname",
    "replicate",
    "block",
    "plotNumber",
    "entryType"
]


def build_cv_datasets(pheno, focal_trial, cv_type):
    """
    Build CV0 or CV00 datasets for a given focal trial.
    Always returns:
        train_pheno, train_trials, train_accessions, test_accessions
    """

    # ------------------------------------------------------------
    # 1. Extract phenotype rows for the focal trial
    # ------------------------------------------------------------
    focal_pheno = pheno[pheno["studyName"] == focal_trial]

    # ------------------------------------------------------------
    # 2. If no phenotype rows exist, fall back to genotype-only prediction
    # ------------------------------------------------------------
    if focal_pheno.empty:
        print(f"⚠ No phenotype rows found for {focal_trial}. Using all other trials for training.")

        train_pheno = pheno.copy()
        train_trials = train_pheno["studyName"].unique().tolist()
        train_accessions = train_pheno["germplasmName"].unique().tolist()

        # Test = all unique accessions (genotype-only prediction)
        test_accessions = train_accessions.copy()

        return train_pheno, train_trials, train_accessions, test_accessions

    # ------------------------------------------------------------
    # 3. Normal CV0 / CV00 logic when phenotype exists
    # ------------------------------------------------------------
    if cv_type == "CV0":
        train_pheno = pheno[pheno["studyName"] != focal_trial].copy()
        test_pheno = focal_pheno.copy()

    elif cv_type == "CV00":
        focal_accessions = focal_pheno["germplasmName"].unique()

        train_pheno = pheno[
            (pheno["studyName"] != focal_trial) &
            (~pheno["germplasmName"].isin(focal_accessions))
        ].copy()

        test_pheno = focal_pheno.copy()

    else:
        raise ValueError(f"Unknown CV type: {cv_type}")

    # ------------------------------------------------------------
    # 4. Extract required outputs
    # ------------------------------------------------------------
    train_trials = train_pheno["studyName"].unique().tolist()
    train_accessions = train_pheno["germplasmName"].unique().tolist()
    test_accessions = test_pheno["germplasmName"].unique().tolist()

    return train_pheno, train_trials, train_accessions, test_accessions
