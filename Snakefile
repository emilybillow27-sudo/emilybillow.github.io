###############################################
# T3/Wheat Predictathon – Snakemake Pipeline
# Option C: BrAPI for metadata, local genotypes
###############################################

FOCAL_TRIALS = [
    "AWY1_DVPWA_2024",
    "TCAP_2025_MANKS",
    "25_Big6_SVREC_SVREC",
    "OHRWW_2025_SPO",
    "CornellMaster_2025_McGowan",
    "24Crk_AY2-3",
    "2025_AYT_Aurora",
    "YT_Urb_25",
    "STP1_2025_MCG",
]

CV_TYPES = ["CV0", "CV00"]
FILETYPES = ["accessions", "trials", "predictions"]


###############################################
# Rule: all
###############################################
rule all:
    input:
        expand(
            "submission_output/{trial}/{cv}/{cv}{filetype}.csv",
            trial=FOCAL_TRIALS,
            cv=CV_TYPES,
            filetype=FILETYPES
        )


###############################################
# Rule: fetch genotypes (local file, Option C)
###############################################
rule fetch_genotypes_local:
    """
    Load the local Predictathon genotype matrix and normalize accession names.
    """
    input:
        "data/raw/genotypes.csv"
    output:
        "data/raw/genotypes_from_local.csv"
    shell:
        "python src/fetch_t3_genotypes.py"


###############################################
# Rule: preprocess
###############################################
rule preprocess:
    """
    Merge phenotypes, metadata, and local genotype matrix.
    """
    input:
        "data/raw/phenotypes.csv",
        "data/raw/trial_metadata.csv",
        "data/raw/genotypes_from_local.csv"
    output:
        "data/processed/pheno_clean.csv",
        "data/processed/env_descriptors.csv",
        "data/processed/geno_imputed.csv",
        "data/processed/G_matrix.npz"
    shell:
        "python src/preprocess_data.py"


###############################################
# Rule: modeling
###############################################
rule modeling:
    """
    Train models and generate Predictathon submission files.
    """
    input:
        "data/processed/pheno_clean.csv",
        "data/processed/env_descriptors.csv",
        "data/processed/geno_imputed.csv",
        "data/processed/G_matrix.npz",
        "config.yaml"
    output:
        expand(
            "submission_output/{trial}/{cv}/{cv}{filetype}.csv",
            trial=FOCAL_TRIALS,
            cv=CV_TYPES,
            filetype=FILETYPES
        )
    shell:
        "python src/main.py"
