import os
import pandas as pd

def write_submission_files(
    trial_name,
    cv_type,
    preds_df,
    train_trials,
    train_accessions,
    output_root="submission_output"
):
    """
    Write Predictathon submission files into:
        submission_output/{trial}/{cv_type}/
    """

    # Correct directory: include trial_name
    cv_dir = os.path.join(output_root, trial_name, cv_type)
    os.makedirs(cv_dir, exist_ok=True)

    # Accessions
    pd.DataFrame({"accession": train_accessions}).drop_duplicates().to_csv(
        os.path.join(cv_dir, f"{cv_type}accessions.csv"), index=False
    )

    # Trials
    pd.DataFrame({"trial": train_trials}).drop_duplicates().to_csv(
        os.path.join(cv_dir, f"{cv_type}trials.csv"), index=False
    )

    # Predictions
    preds_df.to_csv(
        os.path.join(cv_dir, f"{cv_type}predictions.csv"), index=False
    )

    print(f"✓ Wrote files to {cv_dir}")
