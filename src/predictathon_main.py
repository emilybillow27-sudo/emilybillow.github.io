#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np

from models import fit_model, predict_for_trial, cross_validate_model
from submission import write_submission_files

# Challenge trials for Predictathon
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

    # --------------------------------------------------------------
    # Resolve repo root so all paths are stable
    # --------------------------------------------------------------
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(ROOT, "data", "processed")
    output_root = os.path.join(ROOT, "submission_output")

    # Correct phenotype file
    pheno_path = os.path.join(data_dir, "train_pheno_overlap.csv")
    geno_path = os.path.join(data_dir, "geno_imputed.csv")
    env_path = os.path.join(data_dir, "env_descriptors.csv")
    G_path = os.path.join(data_dir, "G_matrix.npz")

    # --------------------------------------------------------------
    # Step 1: Load processed data
    # --------------------------------------------------------------
    print("\n=== Loading processed data ===")

    pheno = pd.read_csv(pheno_path)
    geno = pd.read_csv(geno_path)
    env = pd.read_csv(env_path)
    G = np.load(G_path)["G"]

    print(f"✓ Training phenotype rows: {len(pheno)}")
    print(f"✓ Genotype matrix shape: {geno.shape}")
    print(f"✓ GRM shape: {G.shape}")

    MODEL_TYPE = "me_gblup"

    # --------------------------------------------------------------
    # Step 2: Ensure submission folder structure exists
    # --------------------------------------------------------------
    print("\n=== Ensuring submission folder structure ===")

    for trial in FOCAL_TRIALS:
        for cv_type in ["CV0", "CV00"]:
            os.makedirs(os.path.join(output_root, trial, cv_type), exist_ok=True)

    # --------------------------------------------------------------
    # Step 3: Run CV1 cross-validation
    # --------------------------------------------------------------
    print("\n=== Running CV1 cross-validation ===")

    cv_results = cross_validate_model(
        train_pheno=pheno,
        geno=geno,
        env=env,
        G=G,
        model_type=MODEL_TYPE,
        n_folds=5,
    )

    # Compute accuracy
    corr = cv_results["value"].corr(cv_results["pred"])
    print(f"CV1 accuracy (Pearson r): {corr:.3f}")

    # Save CV results
    cv_out = os.path.join(output_root, "cv1_results.csv")
    cv_results.to_csv(cv_out, index=False)
    print(f"✓ Saved CV1 results to {cv_out}")

    # --------------------------------------------------------------
    # Step 4: Fit final model on all training data
    # --------------------------------------------------------------
    print("\n=== Fitting final model on all training data ===")

    model = fit_model(
        train_pheno=pheno,
        geno=geno,
        env=env,
        G=G,
        model_type=MODEL_TYPE,
    )

    # --------------------------------------------------------------
    # Step 5: Predict for challenge trials
    # --------------------------------------------------------------
    print("\n=== Predicting for challenge trials ===")

    # env has no accession column → predict for all genotyped lines
    all_genotyped = geno["germplasmName"].unique().tolist()

    for trial in FOCAL_TRIALS:
        for cv_type in ["CV0", "CV00"]:
            print(f"\n--- {trial} / {cv_type} ---")
            print(f"  Predicting for {len(all_genotyped)} genotyped accessions.")

            preds_df = predict_for_trial(
                model=model,
                focal_trial=trial,
                test_accessions=all_genotyped,
                geno=geno,
                env=env,
                G=G,
                model_type=MODEL_TYPE,
            )

            write_submission_files(
                trial_name=trial,
                cv_type=cv_type,
                preds_df=preds_df,
                train_trials=["historical"],
                train_accessions=pheno["germplasmName"].unique().tolist(),
                output_root=output_root,
            )

    print("\n✓ Modeling + submission generation complete.\n")


if __name__ == "__main__":
    main()
