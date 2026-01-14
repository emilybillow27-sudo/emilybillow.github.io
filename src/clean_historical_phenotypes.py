#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# If the file is already in long format, just save it and exit
required_cols = {"germplasmName", "trial", "trait_name", "value"}
if required_cols.issubset(df.columns):
    print("Input already in cleaned long-format. Skipping cleaning.")
    df.to_csv("data/processed/historical_phenotypes_clean.csv", index=False)
    exit(0)

# Input phenotype file (from preprocess_data.py)
raw_path = os.path.join(ROOT, "data", "processed", "preprocessed_final.csv")

# Output cleaned phenotype file
out_path = os.path.join(ROOT, "data", "processed", "historical_phenotypes_clean.csv")

print("Loading:", raw_path)
df = pd.read_csv(raw_path, low_memory=False)

# --------------------------------------------------------------
# 1. Identify all grain yield columns
# --------------------------------------------------------------
yield_cols = [
    col for col in df.columns
    if "Grain yield" in col
]

if not yield_cols:
    raise ValueError("No grain yield columns found in phenotype file.")

print("\nDetected yield columns:")
for c in yield_cols:
    print("  -", c)

# Prefer kg/ha if present
kg_ha_cols = [c for c in yield_cols if "kg/ha" in c]
g_plot_cols = [c for c in yield_cols if "g/plot" in c]

if kg_ha_cols:
    primary_yield = kg_ha_cols[0]
    print(f"\nPrimary yield column (preferred): {primary_yield}")
else:
    primary_yield = yield_cols[0]
    print(f"\nPrimary yield column (fallback): {primary_yield}")

# Secondary yield column (fallback)
secondary_yield = None
if g_plot_cols:
    secondary_yield = g_plot_cols[0]
    print(f"Secondary yield column (fallback): {secondary_yield}")

# --------------------------------------------------------------
# 2. Build a unified yield column
# --------------------------------------------------------------
df["value"] = df[primary_yield]

# If primary is missing, fill from secondary
if secondary_yield:
    df["value"] = df["value"].fillna(df[secondary_yield])

# Drop rows where both are missing
df = df.dropna(subset=["value"])

# --------------------------------------------------------------
# 3. Keep only essential columns
# --------------------------------------------------------------
required_cols = ["studyName", "germplasmName", "value"]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df = df[required_cols].copy()

# Rename to modeling-friendly names
df = df.rename(columns={
    "studyName": "trial",
    "germplasmName": "germplasmName",
    "value": "value"
})

# Add traitName column
df["traitName"] = "grain_yield"

# --------------------------------------------------------------
# 4. Save
# --------------------------------------------------------------
df.to_csv(out_path, index=False)

print(f"\n✓ Clean phenotype file written to {out_path}")
print("Final shape:", df.shape)
print("Unique germplasm:", df['germplasmName'].nunique())
