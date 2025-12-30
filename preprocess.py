"""
preprocess_data.py

Reads raw phenotype, genotype, and trial metadata files from data/raw/,
harmonizes trait names using T3 abbreviations, constructs environment
descriptors, imputes genotypes, builds a genomic relationship matrix (GRM),
and writes all processed outputs to data/processed/.

Directory structure expected:

data/
    raw/
        phenotypes.csv
        trial_metadata.csv
        genotypes.csv
    processed/
        (outputs written here)

Author: Emily Billow
"""

import os
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------
# 1. Trait Abbreviation Map (from T3 Wheat Newsletter)
# ---------------------------------------------------------------------

TRAIT_ABBREV_MAP = {
    "Agronomic score - 1-5 scoring scale": "AG SCORE 1-5",
    "Anthesis time - Julian date (JD)": "ANTH JD",
    "Bacterial leaf streak severity - 0-9 percentage scale": "BLS 0-9",
    "FHB disease index - %": "FHB DI %",
    "FHB DON content - ppm": "DON ppm",
    "FHB grain incidence - %": "FDK %",
    "FHB incidence - %": "FHB INC %",
    "FHB severity - %": "FHB SEV %",
    "Grain moisture content - %": "GRAIN MST %",
    "Grain number per spike - grain/spike": "GN grain/spike",
    "Grain protein content - %": "PROTEIN %",
    "Grain test weight - g/L": "TW g/L",
    "Grain weight - 1000 kernels - g/1000 grain": "TKW g",
    "Grain yield - g/plot": "WGT g",
    "Grain yield - kg/ha": "YLD kg/ha",
    "Heading time - day": "HD DAP",
    "Heading time - Julian date (JD)": "HD JD",
    "Hessian fly damage - 1-9 response scale": "HF 1-9",
    "Leaf rust plant response - 0-9 Mc Neal scale": "LR 0-9",
    "Lodging incidence - %": "LDG %",
    "Lodging incidence - 0-9 percentage scale": "LDG 0-9",
    "Maturity time - physiological - Julian date (JD)": "MAT JD",
    "Plant height - cm": "HT cm",
    "Plant stand - 0-9 density scale": "STAND 0-9",
    "Powdery mildew plant response - 0-10 response scale": "PM 0-10",
    "Stem rust severity - 0-9 percentage scale": "SR 0-9",
    "Stripe rust plant response - 0-9 Mc Neal scale": "YR 0-9",
    "Stripe rust severity - %": "YR SEV %",
    "Winter kill damage - %": "WNTDM %",
    "Winter survival - %": "WNTSUR %",
}

YIELD_TRAIT_ABBREVS = {"YLD kg/ha", "WGT g"}  # You can expand this if needed


# ---------------------------------------------------------------------
# 2. Clean Phenotypes
# ---------------------------------------------------------------------

def clean_phenotypes(pheno: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize trait names, apply abbreviations, filter to yield traits,
    and create env_id.
    """
    pheno = pheno.copy()

    # Map full T3 trait names → abbreviations
    pheno["trait_abbrev"] = pheno["trait_name"].map(TRAIT_ABBREV_MAP).fillna(pheno["trait_name"])

    # Filter to yield traits
    pheno = pheno[pheno["trait_abbrev"].isin(YIELD_TRAIT_ABBREVS)]

    # Build environment identifier
    pheno["env_id"] = (
        pheno["location"].astype(str).str.strip() + "_" +
        pheno["year"].astype(str) + "_" +
        pheno["studyName"].astype(str).str.strip()
    )

    # Basic cleaning
    pheno = pheno.dropna(subset=["value"])  # remove missing observations

    return pheno


# ---------------------------------------------------------------------
# 3. Build Environment Descriptors
# ---------------------------------------------------------------------

def build_env_descriptors(trial_meta: pd.DataFrame) -> pd.DataFrame:
    """
    Build environment-level covariates using T3 trial metadata schema.
    """
    env = trial_meta.copy()

    env["studyName"] = env["trial_name"].astype(str).str.strip()
    env["env_id"] = (
        env["location"].astype(str).str.strip() + "_" +
        env["year"].astype(str) + "_" +
        env["studyName"]
    )

    # Convert dates
    for col in ["planting_date", "harvest_date"]:
        if col in env.columns:
            env[col] = pd.to_datetime(env[col], errors="coerce")

    # Compute plot area if available
    if {"plot_width", "plot_length"}.issubset(env.columns):
        env["plot_area"] = (
            pd.to_numeric(env["plot_width"], errors="coerce") *
            pd.to_numeric(env["plot_length"], errors="coerce")
        )

    keep_cols = [
        "env_id", "studyName", "location", "year",
        "planting_date", "harvest_date",
        "plot_area", "design_type"
    ]

    return env[[c for c in keep_cols if c in env.columns]]


# ---------------------------------------------------------------------
# 4. Genotype Imputation (Simple Placeholder)
# ---------------------------------------------------------------------

def impute_genotypes(geno: pd.DataFrame) -> pd.DataFrame:
    """
    Simple mean imputation for missing genotype calls.
    Replace with Beagle, AlphaImpute, or your preferred method.
    """
    geno = geno.copy()
    marker_cols = geno.columns[1:]  # assume first column is accession ID
    geno[marker_cols] = geno[marker_cols].apply(lambda col: col.fillna(col.mean()))
    return geno


# ---------------------------------------------------------------------
# 5. Build Genomic Relationship Matrix (GRM)
# ---------------------------------------------------------------------

def build_grm(geno: pd.DataFrame) -> np.ndarray:
    """
    Build a simple centered GRM: G = ZZ' / p
    where Z is centered genotype matrix.
    """
    marker_matrix = geno.iloc[:, 1:].values  # numeric genotype matrix
    Z = marker_matrix - marker_matrix.mean(axis=0)
    G = (Z @ Z.T) / Z.shape[1]
    return G


# ---------------------------------------------------------------------
# 6. Main Script
# ---------------------------------------------------------------------

def main():

    RAW = "data/raw/"
    OUT = "data/processed/"
    os.makedirs(OUT, exist_ok=True)

    print("Loading raw data...")

    pheno = pd.read_csv(os.path.join(RAW, "phenotypes.csv"))
    trial_meta = pd.read_csv(os.path.join(RAW, "trial_metadata.csv"))
    geno = pd.read_csv(os.path.join(RAW, "genotypes.csv"))

    print("Cleaning phenotypes...")
    pheno_clean = clean_phenotypes(pheno)
    pheno_clean.to_parquet(os.path.join(OUT, "pheno_clean.parquet"))
    print("✓ pheno_clean.parquet written")

    print("Building environment descriptors...")
    env = build_env_descriptors(trial_meta)
    env.to_parquet(os.path.join(OUT, "env_descriptors.parquet"))
    print("✓ env_descriptors.parquet written")

    print("Imputing genotypes...")
    geno_imp = impute_genotypes(geno)
    geno_imp.to_parquet(os.path.join(OUT, "geno_imputed.parquet"))
    print("✓ geno_imputed.parquet written")

    print("Building GRM...")
    G = build_grm(geno_imp)
    np.savez(os.path.join(OUT, "G_matrix.npz"), G=G)
    print("✓ G_matrix.npz written")

    print("All preprocessing complete.")


if __name__ == "__main__":
    main()
# src/preprocess.py

import pandas as pd

def clean_phenotypes(pheno: pd.DataFrame) -> pd.DataFrame:
    """Standardize trait names, remove outliers, create env_id."""
    pheno = pheno.copy()
    # TODO: unify trait names, filter yield traits
    # TODO: create env_id = location_year_study
    return pheno

def harmonize_germplasm_ids(pheno, geno):
    """Ensure germplasmName matches across phenotype and genotype tables."""
    # TODO: strip whitespace, uppercase, unify naming
    return pheno, geno

def impute_genotypes(geno: pd.DataFrame) -> pd.DataFrame:
    """Simple mean imputation or call external imputation."""
    # TODO: implement
    return geno
