###############################################
# Internal pipeline paths
###############################################

PROCESSED_DIR = "data/processed"

MERGED_GENO   = f"{PROCESSED_DIR}/geno_merged_raw.csv"
PREPROCESSED_FINAL = f"{PROCESSED_DIR}/preprocessed_final.csv"

###############################################
# Rule: merge_genotypes
###############################################

rule merge_genotypes:
    output:
        MERGED_GENO
    shell:
        """
        python src/merge_vcfs.py
        """

###############################################
# Rule: modeling
###############################################

rule modeling:
    input:
        pheno = PREPROCESSED_FINAL,
        geno  = MERGED_GENO,
        config = "config.yaml"
    output:
        directory("submission_output")
    shell:
        """
        python src/main.py
        """

###############################################
# Final target
###############################################

rule all:
    input:
        "submission_output"