"""
submission.py

Creates the exact folder structure required by the T3/Wheat Predictathon.
Writes CV0 and CV00 predictions + metadata files for each focal trial.

Author: Emily Billow
"""

import os
import pandas as pd


def write_submission(pred_df: pd.DataFrame,
                     cv_type: str,
                     focal_env: str,
                     outdir: str = "submission_output"):
    """
    Write predictions and metadata files for a single focal environment.

    Args:
        pred_df: DataFrame with columns:
            germplasmName, final_pred, env_id, trial_name
        cv_type: "CV0" or "CV00"
        focal_env: environment identifier (e.g., "AWY1_DVPWA_2024")
        outdir: base output directory
    """

    trial_dir = os.path.join(outdir, focal_env)
    os.makedirs(trial_dir, exist_ok=True)

    # Required filenames
    pred_file = os.path.join(trial_dir, f"{cv_type}_Predictions.csv")
    trials_file = os.path.join(trial_dir, f"{cv_type}_Trials.csv")
    acc_file = os.path.join(trial_dir, f"{cv_type}_Accessions.csv")

    # Predictions file
    pred_df[["germplasmName", "final_pred"]].rename(
        columns={"final_pred": "predicted_value"}
    ).to_csv(pred_file, index=False)

    # Trials file (single row)
    pd.DataFrame({"trial_name": [focal_env]}).to_csv(trials_file, index=False)

    # Accessions file
    pd.DataFrame({"germplasmName": pred_df["germplasmName"].unique()}).to_csv(
        acc_file, index=False
    )

    print(f"✓ Wrote {cv_type} submission for {focal_env} → {trial_dir}")


def write_all_submissions(results_dict, outdir="submission_output"):
    """
    results_dict structure:
    {
        focal_env: {
            "CV0": pred_df,
            "CV00": pred_df
        },
        ...
    }
    """
    for focal_env, cv_dict in results_dict.items():
        for cv_type, pred_df in cv_dict.items():
            write_submission(pred_df, cv_type, focal_env, outdir)
