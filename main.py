"""
main.py

Master orchestrator for the T3/Wheat Predictathon pipeline.
Runs preprocessing, modeling, CV construction, and submission generation.

Author: Emily Billow
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

def run_preprocessing():
    print("\n=== STEP 1: Preprocessing Data ===")
    script = os.path.join(SRC, "preprocess_data.py")
    subprocess.run([sys.executable, script], check=True)
    print("✓ Preprocessing complete.\n")


def run_modeling():
    print("=== STEP 2: Modeling (placeholder) ===")
    # Example:
    # subprocess.run([sys.executable, os.path.join(SRC, "models.py")], check=True)
    print("Modeling step not yet implemented.\n")


def run_cv_and_submission():
    print("=== STEP 3: CV0/CV00 + Submission (placeholder) ===")
    # Example:
    # subprocess.run([sys.executable, os.path.join(SRC, "submission.py")], check=True)
    print("Submission generation not yet implemented.\n")


def main():
    print("==========================================")
    print("   T3/Wheat Predictathon Pipeline Runner   ")
    print("==========================================\n")

    run_preprocessing()
    run_modeling()
    run_cv_and_submission()

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()

__________________________________________________________
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
