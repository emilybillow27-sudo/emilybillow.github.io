# Snakefile for T3/Wheat Predictathon Pipeline

RAW = "data/raw"
PROCESSED = "data/processed"
SRC = "src"

rule all:
    input:
        f"{PROCESSED}/pheno_clean.parquet",
        f"{PROCESSED}/env_descriptors.parquet",
        f"{PROCESSED}/geno_imputed.parquet",
        f"{PROCESSED}/G_matrix.npz"

rule preprocess:
    input:
        phenotypes=f"{RAW}/phenotypes.csv",
        trial_meta=f"{RAW}/trial_metadata.csv",
        genotypes=f"{RAW}/genotypes.csv"
    output:
        pheno_clean=f"{PROCESSED}/pheno_clean.parquet",
        env_desc=f"{PROCESSED}/env_descriptors.parquet",
        geno_imp=f"{PROCESSED}/geno_imputed.parquet",
        grm=f"{PROCESSED}/G_matrix.npz"
    shell:
        """
        python {SRC}/preprocess_data.py
        """

