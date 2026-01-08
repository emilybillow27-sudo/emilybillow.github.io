import pandas as pd

# Load phenotype and merged genotype matrix
pheno = pd.read_csv("data/processed/modeling_matrix.csv")
geno = pd.read_csv("data/processed/geno_merged_raw.csv")

# Keep only accessions present in phenotype file
valid = set(pheno["germplasmName"])
filtered = geno[geno["germplasmName"].isin(valid)]

print("Before filtering:", geno.shape)
print("After filtering:", filtered.shape)

filtered.to_csv("data/processed/geno_filtered.csv", index=False)
print("✓ Saved filtered genotype matrix to data/processed/geno_filtered.csv")
