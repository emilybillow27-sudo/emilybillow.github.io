# Snakefile for T3/Wheat Predictathon Pipeline

RAW = "data/raw"
PROCESSED = "data/processed"
SRC = "src"

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


# ---------------------------------------------------------------------
# Final target: require all submission files to exist
# ---------------------------------------------------------------------
rule all:
    input:
        expand(
            "submission_output/{trial}/{cv}/{cv}{filetype}.csv",
            trial=FOCAL_TRIALS,
            cv=CV_TYPES,
            filetype=["accessions", "trials", "predictions"]
        )


# ---------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# Modeling
# ---------------------------------------------------------------------
rule modeling:
    input:
        pheno=f"{PROCESSED}/pheno_clean.csv",
        env=f"{PROCESSED}/env_descriptors.csv",
        geno=f"{PROCESSED}/geno_imputed.csv",
        grm=f"{PROCESSED}/G_matrix.npz",
        config="config.yaml"
    output:
        expand(
            "submission_output/{trial}/{cv}/{cv}{filetype}.csv",
            trial=FOCAL_TRIALS,
            cv=["CV0", "CV00"],
            filetype=["accessions", "trials", "predictions"]
        )
    shell:
        """
        python {SRC}/main.py
        """
# ---------------------------------------------------------------------