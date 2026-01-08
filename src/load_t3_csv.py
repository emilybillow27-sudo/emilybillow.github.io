# src/load_t3_csv.py
import pandas as pd
import os

def load_t3_csv(path, chunksize=5000, out_path="data/processed/preprocessed.csv"):
    """
    Stream a massive T3 phenotype_download.csv file safely.
    - Reads in chunks
    - Melts each chunk
    - Writes directly to disk (no RAM buildup)
    - Never concatenates in memory
    """

    print(f"Streaming large CSV file in chunks: {path}")

    # -----------------------------
    # First pass: read ONLY the header
    # -----------------------------
    header_df = pd.read_csv(path, nrows=0)
    all_columns = list(header_df.columns)

    # Identify metadata vs trait columns
    metadata_cols = [
        "studyYear", "programDbId", "programName", "programDescription",
        "studyDbId", "studyName", "studyDescription", "studyDesign",
        "plotWidth", "plotLength", "fieldSize",
        "fieldTrialIsPlannedToBeGenotyped", "fieldTrialIsPlannedToCross",
        "plantingDate", "harvestDate",
        "locationDbId", "locationName",
        "germplasmDbId", "germplasmName", "germplasmSynonyms",
        "observationLevel", "observationUnitDbId", "observationUnitName",
        "replicate", "blockNumber", "plotNumber", "rowNumber", "colNumber",
        "entryType", "plantNumber",
        "plantedSeedlotStockDbId", "plantedSeedlotStockUniquename",
        "plantedSeedlotCurrentCount", "plantedSeedlotCurrentWeightGram",
        "plantedSeedlotBoxName", "plantedSeedlotTransactionCount",
        "plantedSeedlotTransactionWeight", "plantedSeedlotTransactionDescription",
        "availableGermplasmSeedlotUniquenames"
    ]

    metadata_cols = [c for c in metadata_cols if c in all_columns]
    trait_cols = [c for c in all_columns if c not in metadata_cols]

    print(f"Detected {len(metadata_cols)} metadata columns")
    print(f"Detected {len(trait_cols)} trait columns")

    # -----------------------------
    # Parse trait metadata once
    # -----------------------------
    parsed_traits = []
    for col in trait_cols:
        parts = col.split("|")
        base_name = parts[0].strip()
        timepoint = None
        trait_id = None

        for p in parts[1:]:
            p = p.strip()
            if p.startswith("day") or p.startswith("timepoint"):
                timepoint = p
            elif "CO_" in p or "COMP:" in p:
                trait_id = p

        parsed_traits.append({
            "trait_full": col,
            "trait_base": base_name,
            "timepoint": timepoint,
            "trait_id": trait_id
        })

    trait_info = pd.DataFrame(parsed_traits)

    # -----------------------------
    # Prepare output file
    # -----------------------------
    if os.path.exists(out_path):
        os.remove(out_path)

    print(f"Writing output to: {out_path}")
    first_chunk = True

    # -----------------------------
    # Stream chunks → melt → write
    # -----------------------------
    print("Beginning streaming processing...")

    for chunk_idx, chunk in enumerate(
        pd.read_csv(path, chunksize=chunksize, dtype=str, on_bad_lines="skip")
    ):
        print(f"Processing chunk {chunk_idx + 1}...")

        # Melt wide → long
        long_df = chunk.melt(
            id_vars=metadata_cols,
            value_vars=trait_cols,
            var_name="trait_full",
            value_name="value"
        )

        # Merge trait metadata
        long_df = long_df.merge(trait_info, on="trait_full", how="left")

        # Append to disk
        long_df.to_csv(
            out_path,
            mode="a",
            header=first_chunk,
            index=False
        )

        first_chunk = False  # Only write header once

    print("Finished streaming CSV.")
    print(f"Final output written to {out_path}")

    # Return nothing — data is already on disk
    return None
