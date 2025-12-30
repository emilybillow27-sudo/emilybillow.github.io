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
