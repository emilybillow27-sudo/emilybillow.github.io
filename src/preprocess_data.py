#!/usr/bin/env python3
import argparse
import os
import pandas as pd
from tqdm import tqdm


############################################################
# Utility: Stream CSV in chunks with progress bar
############################################################
def stream_csv_with_progress(path, chunksize=50000, desc="Streaming CSV"):
    total_bytes = os.path.getsize(path)
    with open(path, "rb") as f:
        with tqdm(total=total_bytes, unit="B", unit_scale=True, desc=desc) as pbar:
            for chunk in pd.read_csv(path, chunksize=chunksize):
                pbar.update(f.tell() - pbar.n)
                yield chunk


############################################################
# Processing functions (customize as needed)
############################################################
def process_raw_chunk(chunk):
    """
    First-pass cleaning.
    Add your filtering, renaming, NA handling, etc. here.
    """
    return chunk


def fetch_trait_metadata():
    """
    Optional: load trait metadata if you use it.
    Return an empty dict if not needed.
    """
    return {}


def harmonize_trait_names(chunk, trait_metadata):
    """
    Second-pass harmonization.
    Add trait renaming or mapping logic here.
    """
    return chunk


############################################################
# MAIN PIPELINE
############################################################
def main():
    parser = argparse.ArgumentParser(description="Preprocess phenotype CSV into clean modeling-ready files")
    parser.add_argument("--pheno", required=True, help="Path to phenotype CSV")
    parser.add_argument("--meta", required=False, help="(Optional) metadata CSV")
    parser.add_argument("--geno", required=False, help="(Optional) genotype CSV")
    args = parser.parse_args()

    raw_path = args.pheno

    # Output locations
    processed_path = "data/processed/preprocessed.csv"
    final_path = "data/processed/preprocessed_final.csv"

    print("\n=== PASS 1: Processing raw phenotype CSV ===")
    first = True

    for chunk in stream_csv_with_progress(raw_path, desc="Processing raw CSV"):
        chunk = process_raw_chunk(chunk)

        chunk.to_csv(
            processed_path,
            mode="w" if first else "a",
            header=first,
            index=False
        )
        first = False

    print(f"Finished streaming raw CSV → {processed_path}")

    print("\nFetching trait metadata...")
    trait_metadata = fetch_trait_metadata()
    print("Trait metadata loaded.")

    print("\n=== PASS 2: Harmonizing processed phenotype CSV ===")
    first = True

    for chunk in stream_csv_with_progress(processed_path, desc="Harmonizing CSV"):
        chunk = harmonize_trait_names(chunk, trait_metadata)

        chunk.to_csv(
            final_path,
            mode="w" if first else "a",
            header=first,
            index=False
        )
        first = False

    print(f"\nFinal output written to {final_path}")
    print("Preprocessing pipeline completed successfully.")


############################################################
# Entry point
############################################################
if __name__ == "__main__":
    main()