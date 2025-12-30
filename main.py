# src/main.py

import pandas as pd
from cv_protocols import build_cv_datasets
from models import fit_model, predict_for_trial
from submission import write_submission_files

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

def main():

    # Load processed data
    pheno = pd.read_parquet("data/processed/pheno_clean.parquet")
    geno = pd.read_parquet("data/processed/geno_imputed.parquet")
    env = pd.read_parquet("data/processed/env_descriptors.parquet")

    for trial in FOCAL_TRIALS:
        for cv_type in ["CV0", "CV00"]:

            train_pheno, train_trials, train_accessions, test_accessions = \
                build_cv_datasets(pheno, trial, cv_type)

            model = fit_model(train_pheno, geno, env)

            preds_df = predict_for_trial(
                model=model,
                focal_trial=trial,
                test_accessions=test_accessions,
                geno=geno,
                env=env
            )

            write_submission_files(
                trial_name=trial,
                cv_type=cv_type,
                preds_df=preds_df,
                train_trials=train_trials,
                train_accessions=train_accessions,
                output_root="submission_output"
            )

if __name__ == "__main__":
    main()
