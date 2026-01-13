import allel
import pandas as pd
import numpy as np
import glob
import os

# Path to your real genotype directory
RAW_DIR = "/Users/emilybillow/Desktop/emilybillow_data/raw"

# Detect ALL VCFs in that folder (both .vcf and .vcf.gz)
vcf_paths = sorted(
    glob.glob(os.path.join(RAW_DIR, "*.vcf")) +
    glob.glob(os.path.join(RAW_DIR, "*.vcf.gz"))
)

print("Found VCFs:")
for p in vcf_paths:
    print("  ", p)

if len(vcf_paths) == 0:
    raise FileNotFoundError(f"No VCFs found in {RAW_DIR}")

all_geno = []
all_samples = set()

# Step 1: read each VCF
for vcf in vcf_paths:
    print(f"\nReading {vcf}")
    callset = allel.read_vcf(vcf, fields=["samples", "calldata/GT", "variants/ID"])

    samples = callset["samples"]
    gt = allel.GenotypeArray(callset["calldata/GT"]).to_n_alt()
    markers = callset["variants/ID"]

    # Prefix markers with filename to avoid collisions
    prefix = os.path.basename(vcf).replace(".vcf", "").replace(".gz", "")
    markers = [f"{prefix}_{m}" for m in markers]

    df = pd.DataFrame(gt.T, columns=markers)
    df.insert(0, "germplasmName", samples)

    all_geno.append(df)
    all_samples.update(samples)

# Step 2: union of all samples across all VCFs
all_samples = sorted(list(all_samples))
merged = pd.DataFrame({"germplasmName": all_samples})

# Step 3: merge each VCF matrix (union mode)
for df in all_geno:
    merged = merged.merge(df, on="germplasmName", how="left")

# Step 4: save merged genotype matrix
output_path = "data/processed/geno_merged_raw.csv"
merged.to_csv(output_path, index=False)

print("\n✓ Merged genotype matrix written to:", output_path)
print("Final shape:", merged.shape)
print("Unique accessions:", merged['germplasmName'].nunique())