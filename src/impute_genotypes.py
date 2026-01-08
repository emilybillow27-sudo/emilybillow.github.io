import pandas as pd
from sklearn.impute import SimpleImputer

geno = pd.read_csv("data/processed/geno_filtered.csv")

X = geno.drop(columns=["germplasmName"])

print("Genotype matrix shape:", X.shape)
print("Genotype matrix head:")
print(X.head())

imp = SimpleImputer(strategy="most_frequent")
X_imp = imp.fit_transform(X)

geno_imp = pd.DataFrame(X_imp, columns=X.columns)
geno_imp.insert(0, "germplasmName", geno["germplasmName"])

geno_imp.to_csv("data/processed/geno_imputed.csv", index=False)

print("Imputed genotype matrix shape:", geno_imp.shape)