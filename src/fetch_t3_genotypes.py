"""
Load genotype data from the local Predictathon dataset.

T3/Wheat does not expose genotype endpoints via BrAPI, so we rely on the
provided genotype matrix instead. This script simply loads the local file,
harmonizes accession names if needed, and writes it to the raw directory.

Outputs:
    data/raw/genotypes_from_local.csv
"""

import pandas as pd

GENO_INPUT = "data/raw/genotypes.csv"   # provided by Predictathon
GENO_OUTPUT = "data/raw/genotypes_from_local.csv"


def main():

    print("Loading local genotype matrix...")
    geno = pd.read_csv(GENO_INPUT)

    print(f"Genotype matrix loaded with shape: {geno.shape}")

    # Optional: normalize accession column names
    possible_cols = ["germplasm_name", "germplasmName", "accession", "GID", "line_name"]
    acc_col = next((c for c in possible_cols if c in geno.columns), None)

    if acc_col is None:
        print("Warning: No accession column detected. Proceeding without renaming.")
    else:
        print(f"Using accession column: {acc_col}")
        geno = geno.rename(columns={acc_col: "accession"})

    geno.to_csv(GENO_OUTPUT, index=False)
    print(f"✓ Saved genotype matrix to {GENO_OUTPUT}")


if __name__ == "__main__":
    main()
