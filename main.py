import os
import pandas as pd
import numpy as np
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

    # Load processed data (CSV instead of Parquet)
    pheno = pd.read_csv("data/processed/pheno_clean.csv")
    geno = pd.read_csv("data/processed/geno_imputed.csv")
    env = pd.read_csv("data/processed/env_descriptors.csv")
    G = np.load("data/processed/G_matrix.npz")["G"]

    # Detect metadata-only mode
    metadata_only = (
        pheno.empty or
        env.empty or
        geno.shape[1] <= 1 or
        G.size == 0
    )

    if metadata_only:
        print("\n⚠ Metadata-only mode detected — skipping modeling.")
        print("   (No phenotypes, no markers, or no environment descriptors.)\n")

        # Still create empty submission folders for each trial + CV type
        for trial in FOCAL_TRIALS:
            for cv_type in ["CV0", "CV00"]:
                os.makedirs(f"submission_output/{trial}/{cv_type}", exist_ok=True)

        print("✓ Empty submission structure created.\n")
        return

    # ------------------------------------------------------------------
    # Full modeling path (will run automatically once real data exists)
    # ------------------------------------------------------------------

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

    print("\n✓ Modeling + submission generation complete.\n")


if __name__ == "__main__":
    main()
