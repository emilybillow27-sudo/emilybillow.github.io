"""
main.py

Master orchestrator for the T3/Wheat Predictathon pipeline.
Runs preprocessing, modeling, CV construction, and submission generation.

Author: Emily Billow
"""

import os
import subprocess
import sys
import pandas as pd
import numpy as np
import yaml

from cv_protocols import build_cv0, build_cv00
from models import fit_and_predict
from submission import write_all_submissions


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")


# ---------------------------------------------------------
# STEP 1 — Preprocessing
# ---------------------------------------------------------

def run_preprocessing():
    print("\n=== STEP 1: Preprocessing Data ===")
    script = os.path.join(SRC, "preprocess_data.py")
    subprocess.run([sys.executable, script], check=True)
    print("✓ Preprocessing complete.\n")


# ---------------------------------------------------------
# STEP 2 — Modeling + Submission
# ---------------------------------------------------------

def run_modeling_and_submission():
    print("=== STEP 2: Modeling + Submission Generation ===")

    # Load config
    with open(os.path.join(ROOT, "config.yaml"), "r") as f:
        cfg = yaml.safe_load(f)

    focal_trials = cfg["focal_trials"]
    use_ml = cfg["model"]["use_ml"]
    trait_col = cfg["traits"]["target_trait"]

    # Load processed data
    pheno = pd.read_parquet(os.path.join(ROOT, "data/processed/pheno_clean.parquet"))
    geno = pd.read_parquet(os.path.join(ROOT, "data/processed/geno_imputed.parquet"))
    G = np.load(os.path.join(ROOT, "data/processed/G_matrix.npz"))["G"]

    results = {}

    for focal_env in focal_trials:
        print(f"\n--- Modeling for focal environment: {focal_env} ---")

        # CV0
        cv0_data = build_cv0(pheno, geno, focal_env)
        cv0_pred = fit_and_predict(cv0_data, G, trait_col, use_ml)
        cv0_pred["env_id"] = focal_env
        cv0_pred["trial_name"] = focal_env

        # CV00
        cv00_data = build_cv00(pheno, geno, focal_env)
        cv00_pred = fit_and_predict(cv00_data, G, trait_col, use_ml)
        cv00_pred["env_id"] = focal_env
        cv00_pred["trial_name"] = focal_env

        results[focal_env] = {
            "CV0": cv0_pred,
            "CV00": cv00_pred
        }

    write_all_submissions(results)
    print("\n✓ Modeling + submission generation complete.\n")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():
    print("==========================================")
    print("   T3/Wheat Predictathon Pipeline Runner   ")
    print("==========================================\n")

    run_preprocessing()
    run_modeling_and_submission()

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()

