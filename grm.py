# src/grm.py

import numpy as np
import pandas as pd

def build_grm(geno: pd.DataFrame) -> np.ndarray:
    """Construct genomic relationship matrix from marker matrix."""
    M = geno.values.astype(float)
    p = np.nanmean(M / 2.0, axis=0)
    std = np.sqrt(2 * p * (1 - p))
    M_std = (M - 2 * p) / std
    M_std = np.nan_to_num(M_std)
    G = (M_std @ M_std.T) / M_std.shape[1]
    return G
