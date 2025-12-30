# src/submission.py

import os
import pandas as pd

def write_submission_files(trial_name, cv_type, preds_df,
                           train_trials, train_accessions, output_root):

    trial_dir = os.path.join(output_root, trial_name)
    os.makedirs(trial_dir, exist_ok=True)

    preds_df.to_csv(os.path.join(trial_dir, f"{cv_type}_Predictions.csv"), index=False)

    pd.DataFrame({"studyName": train_trials}).to_csv(
        os.path.join(trial_dir, f"{cv_type}_Trials.csv"), index=False
    )

    pd.DataFrame({"germplasmName": train_accessions}).to_csv(
        os.path.join(trial_dir, f"{cv_type}_Accessions.csv"), index=False
    )
