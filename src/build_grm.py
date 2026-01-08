#!/usr/bin/env python3

import pandas as pd
import numpy as np

# Load imputed genotype matrix
geno = pd.read_csv("data/processed/geno_imputed.csv")

# Extract marker matrix (0/1/2)
M = geno.drop(columns=["germplasmName"]).values.astype(float)

# Compute allele frequencies p
p = M.mean(axis=0) / 2.0   # because markers coded 0/1/2

# Center markers: Z = M - 2p
Z = M - 2 * p

# Denominator: 2 * sum(p(1-p))
denom = 2 * np.sum(p * (1 - p))

# VanRaden GRM
G = (Z @ Z.T) / denom

# Save GRM with line order
np.savez(
    "data/processed/G_matrix.npz",
    G=G,
    lines=geno["germplasmName"].tolist()
)

print("✓ VanRaden GRM built and saved to data/processed/G_matrix.npz")