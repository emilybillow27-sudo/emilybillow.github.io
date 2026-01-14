#!/bin/bash
set -euo pipefail

echo "======================================"
echo "  T3/Wheat Predictathon Pipeline"
echo "======================================"

# ---------------------------------------------------------
# Optional cleaning step
# Usage: ./run_pipeline.sh --clean
# ---------------------------------------------------------
if [[ "${1:-}" == "--clean" ]]; then
    echo "Cleaning workspace..."
    rm -rf data/processed/*
    rm -rf submission_output/*
    rm -rf .snakemake
    echo "Clean-all complete."
    echo "--------------------------------------"
fi

# ---------------------------------------------------------
# Step 1: Modeling
# ---------------------------------------------------------
echo "Running modeling..."
snakemake modeling -p -j1
echo "--------------------------------------"

# ---------------------------------------------------------
# Step 2: Build all submission files
# ---------------------------------------------------------
echo "Building final submission outputs..."
snakemake all -p -j1
echo "--------------------------------------"

echo "======================================"
echo " Pipeline complete!"
echo "======================================"