#!/usr/bin/env python3

import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_path = os.path.join(ROOT, "data", "raw", "historical_phenotypes.csv")
out_path = os.path.join(ROOT, "data", "processed", "historical_phenotypes_clean.csv")

print("Loading:", raw_path)
df = pd.read_csv(raw_path, low_memory=False)

# --------------------------------------------------------------
# 1. Identify the correct grain yield column
# --------------------------------------------------------------
yield_col = "Grain yield - kg/ha|CO_321:0001218"

if yield_col not in df.columns:
    raise ValueError(f"Yield column not found: {yield_col}")

print(f"Using yield column: {yield_col}")

# --------------------------------------------------------------
# 2. Keep only essential columns
# --------------------------------------------------------------
keep_cols = ["studyName", "germplasmName", yield_col]
df = df[keep_cols].copy()

# Rename to modeling-friendly names
df = df.rename(columns={
    yield_col: "value",
    "studyName": "studyName",
    "germplasmName": "germplasmName"
})

# Add traitName column
df["traitName"] = "Grain yield - kg/ha"

# --------------------------------------------------------------
# 3. Drop missing values
# --------------------------------------------------------------
df = df.dropna(subset=["value"])

# --------------------------------------------------------------
# 4. Save
# --------------------------------------------------------------
df.to_csv(out_path, index=False)
print(f"\n✓ Clean historical phenotype file written to {out_path}")
print("Final shape:", df.shape)
