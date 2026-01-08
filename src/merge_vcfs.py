import allel
import pandas as pd
import numpy as np
import glob
import os

# Automatically detect all VCFs in the folder
vcf_paths = glob.glob("data/raw/breedbase_grm_DPASN.vcf")
print("Found VCFs:", vcf_paths)

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
    prefix = os.path.basename(vcf).replace(".vcf", "")
    markers = [f"{prefix}_{m}" for m in markers]

    df = pd.DataFrame(gt.T, columns=markers)
    df.insert(0, "germplasmName", samples)

    all_geno.append(df)
    all_samples.update(samples)

# Step 2: union all samples
all_samples = sorted(list(all_samples))
merged = pd.DataFrame({"germplasmName": all_samples})

# Step 3: merge each VCF matrix
for df in all_geno:
    merged = merged.merge(df, on="germplasmName", how="left")

# Step 4: save raw merged
output_path = "data/processed/geno_merged_raw.csv"
merged.to_csv(output_path, index=False)

print("\n✓ Merged genotype matrix written to:", output_path)
print("Final shape:", merged.shape)
