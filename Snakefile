###############################################
# External raw data (your Desktop folder)
###############################################

RAW_PHENO = "/Users/emilybillow/Desktop/emilybillow_data/processed/preprocessed_final.csv"
RAW_META  = "/Users/emilybillow/Desktop/emilybillow_data/raw/trial_metadata.csv"
RAW_GENO_DIR = "/Users/emilybillow/Desktop/emilybillow_data/raw"

###############################################
# Internal pipeline paths
###############################################

PROCESSED_DIR = "data/processed"

MERGED_GENO   = f"{PROCESSED_DIR}/geno_merged_raw.csv"
PREPROCESSED  = f"{PROCESSED_DIR}/preprocessed.csv"
PREPROCESSED_FINAL = f"{PROCESSED_DIR}/preprocessed_final.csv"

###############################################
# Rule: merge_genotypes
# Runs src/merge_vcfs.py and produces geno_merged_raw.csv
###############################################

rule merge_genotypes:
    output:
        MERGED_GENO
    shell:
        """
        python src/merge_vcfs.py
        """

###############################################
# Rule: preprocess
# Runs your new preprocess_data.py
# Produces:
#   - preprocessed.csv
#   - preprocessed_final.csv
###############################################

rule preprocess:
    input:
        pheno = RAW_PHENO,
        meta  = RAW_META,
        geno  = MERGED_GENO
    output:
        PREPROCESSED,
        PREPROCESSED_FINAL
    shell:
        """
        python src/preprocess_data.py \
            --pheno {input.pheno} \
            --meta {input.meta} \
            --geno {input.geno}
        """

###############################################
# Rule: modeling
# Uses preprocessed_final.csv as phenotype input
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
