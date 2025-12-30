# Snakefile for T3/Wheat Predictathon Pipeline

RAW = "data/raw"
PROCESSED = "data/processed"
SRC = "src"

rule all:
    input:
        "submission_output"

rule preprocess:
    input:
        phenotypes=f"{RAW}/phenotypes.csv",
        trial_meta=f"{RAW}/trial_metadata.csv",
        genotypes=f"{RAW}/genotypes.csv"
    output:
        pheno_clean=f"{PROCESSED}/pheno_clean.csv",
        env_desc=f"{PROCESSED}/env_descriptors.csv",
        geno_imp=f"{PROCESSED}/geno_imputed.csv",
        grm=f"{PROCESSED}/G_matrix.npz"
    shell:
        """
        python {SRC}/preprocess_data.py
        """

rule modeling:
    input:
        pheno=f"{PROCESSED}/pheno_clean.csv",
        env=f"{PROCESSED}/env_descriptors.csv",
        geno=f"{PROCESSED}/geno_imputed.csv",
        grm=f"{PROCESSED}/G_matrix.npz",
        config="config.yaml"
    output:
        directory("submission_output")
    shell:
        """
        python src/main.py
        """
