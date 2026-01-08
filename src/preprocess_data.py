#!/usr/bin/env python3

import os
import pandas as pd
from tqdm import tqdm


# ============================================================
# Streaming CSV readers
# ============================================================

def stream_csv_with_progress(path, chunksize=200000, desc="Streaming CSV"):
    """
    Stream a CSV file with a byte-accurate progress bar.
    Uses the file handle to track bytes consumed.
    """
    total_bytes = os.path.getsize(path)

    with open(path, "rb") as f, tqdm(
        total=total_bytes,
        unit="B",
        unit_scale=True,
        desc=desc
    ) as pbar:
        reader = pd.read_csv(f, chunksize=chunksize)

        for chunk in reader:
            # Update progress bar based on file pointer movement
            pbar.update(f.tell() - pbar.n)
            yield chunk


# ============================================================
# Placeholder transformation functions
# (Replace with your actual logic)
# ============================================================

def process_raw_chunk(chunk):
    """
    Apply your raw phenotype preprocessing here.
    Example: cleaning, renaming, filtering, type conversion.
    """
    # Example placeholder:
    # chunk = chunk.rename(columns={"old": "new"})
    return chunk


def harmonize_trait_names(chunk, trait_metadata):
    """
    Apply trait harmonization using metadata.
    Replace this with your actual harmonization logic.
    """
    # Example placeholder:
    # chunk["trait"] = chunk["trait"].map(trait_metadata)
    return chunk


def fetch_trait_metadata():
    """
    Fetch trait metadata from BrAPI or local cache.
    Replace with your actual implementation.
    """
    # Placeholder: return empty dict
    return {}


# ============================================================
# Main pipeline
# ============================================================

def main():

    # *** UPDATED FILE NAME HERE ***
    raw_path = "data/raw/2026-01-05T190050phenotype_download.csv"

    processed_path = "data/processed/preprocessed.csv"
    final_path = "data/processed/preprocessed_final.csv"

    # ------------------------------------------------------------
    # 1. STREAM RAW FILE → PROCESS → WRITE PROCESSED FILE
    # ------------------------------------------------------------
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

    print(f"Finished streaming raw CSV. Output written to {processed_path}")

    # ------------------------------------------------------------
    # 2. LOAD TRAIT METADATA
    # ------------------------------------------------------------
    print("\nFetching trait metadata...")
    trait_metadata = fetch_trait_metadata()
    print("Trait metadata loaded.")

    # ------------------------------------------------------------
    # 3. STREAM PROCESSED FILE → HARMONIZE TRAITS → WRITE FINAL FILE
    # ------------------------------------------------------------
    print("\n=== PASS 2: Harmonizing processed phenotype CSV ===")

    first = True
    for chunk in stream_csv_with_progress(processed_path, desc="Reloading processed CSV"):

        chunk = harmonize_trait_names(chunk, trait_metadata)

        chunk.to_csv(
            final_path,
            mode="w" if first else "a",
            header=first,
            index=False
        )
        first = False

    print(f"\nFinal output written to {final_path}")
    print("Pipeline completed successfully.")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()
