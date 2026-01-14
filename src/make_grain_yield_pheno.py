#!/usr/bin/env python3

import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pheno_path = os.path.join(ROOT, "data", "processed", "historical_phenotypes_clean.csv")
geno_path = os.path.join(ROOT, "data", "processed", "geno_merged_raw.csv")

out_pheno_overlap = os.path.join(ROOT, "data", "processed", "train_pheno_overlap.csv")
out_accession_status = os.path.join(ROOT, "data", "processed", "accession_status.csv")

print("Loading phenotype:", pheno_path)
pheno = pd.read_csv(pheno_path)

print("Loading genotype:", geno_path)
geno = pd.read_csv(geno_path)

# assume first column of genotype is germplasm name / line ID
geno_col0 = geno.columns[0]
geno_accessions = set(geno[geno_col0].astype(str))
pheno_accessions = set(pheno["germplasmName"].astype(str))

overlap = pheno_accessions & geno_accessions
only_pheno = pheno_accessions - geno_accessions
only_geno = geno_accessions - pheno_accessions

print(f"\nOverlapping accessions: {len(overlap)}")
print(f"Phenotype-only: {len(only_pheno)}")
print(f"Genotype-only: {len(only_geno)}")

# filter phenotype to overlapping accessions
pheno_overlap = pheno[pheno["germplasmName"].astype(str).isin(overlap)].copy()

# rename to exactly what the modeling code expects
# columns now: germplasmName, trial, value, traitName
expected_cols = ["germplasmName", "trial", "value", "traitName"]
missing = [c for c in expected_cols if c not in pheno_overlap.columns]
if missing:
    raise ValueError(f"Missing expected columns in pheno_overlap: {missing}")

pheno_overlap = pheno_overlap[expected_cols].copy()

pheno_overlap.to_csv(out_pheno_overlap, index=False)
print(f"\n✓ Wrote modeling-ready phenotype (overlap only) to {out_pheno_overlap}")
print("Shape:", pheno_overlap.shape)

# write accession status table (nice for diagnostics)
status_rows = []

for g in sorted(overlap):
    status_rows.append({"germplasmName": g, "status": "both"})

for g in sorted(only_pheno):
    status_rows.append({"germplasmName": g, "status": "phenotype_only"})

for g in sorted(only_geno):
    status_rows.append({"germplasmName": g, "status": "genotype_only"})

status_df = pd.DataFrame(status_rows)
status_df.to_csv(out_accession_status, index=False)
print(f"✓ Wrote accession status table to {out_accession_status}")
print("Done.")
