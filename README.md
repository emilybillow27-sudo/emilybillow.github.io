# emilybillow.github.io
Developing genomic prediction pipelines, G×E models, and tools for wheat breeding.

T3/Wheat Predictathon – Genomic Prediction Pipeline
A Python-based multi-environment genomic prediction framework for CV0 and CV00 evaluation

Overview
This repository contains a fully reproducible pipeline developed for the Triticeae Toolbox (T3/Wheat) Prediction Challenge.
The goal is to predict grain yield for wheat accessions across nine focal trials under the CV0 and CV00 cross-validation scenarios described by Jarquín et al. (2017).

The pipeline:

- Retrieves and preprocesses phenotypic and genotypic data

- Harmonizes germplasm identifiers

- Constructs genomic relationship matrices (GRMs)

- Fits multi-environment genomic prediction models

- Generates predictions for all genotyped accessions in each focal trial

- Produces the required submission folder structure and CSV files

Repository Structure
Code
t3_predictathon/
│
├── data/
│   ├── raw/                # Raw T3/Wheat downloads (phenotypes, genotypes, metadata)
│   └── processed/          # Cleaned phenotypes, imputed genotypes, GRM, env descriptors
│
├── src/
│   ├── t3_io.py            # Data loading / BrAPI access (optional)
│   ├── preprocess.py       # Cleaning, harmonization, imputation
│   ├── grm.py              # Genomic relationship matrix construction
│   ├── models.py           # GBLUP-G×E + ML ensemble models
│   ├── cv_protocols.py     # CV0 and CV00 dataset construction
│   ├── submission.py       # Writes required CSVs for each trial
│   └── main.py             # Master pipeline orchestrator
│
├── submission_output/      # Auto-generated competition submission folder
│
├── methods/                # Draft of methods description for submission
│
├── docs/                   # Notes on T3 challenge, BrAPI endpoints, etc.
│
├── requirements.txt
└── README.md

Getting Started
1. Clone the repository
Code
git clone https://github.com/<your-username>/t3_predictathon.git
cd t3_predictathon
2. Install dependencies
Code
pip install -r requirements.txt
3. Prepare data
Place downloaded T3/Wheat phenotype and genotype files into:

Code
data/raw/
Then run your preprocessing script (example):

Code
python src/preprocess_data.py
This will generate:

pheno_clean.parquet

geno_imputed.parquet

G_matrix.npz

env_descriptors.parquet

in data/processed/.

Modeling Approach
This pipeline implements:

1. Multi-environment GBLUP with G×E
Genotype effects modeled using a genomic relationship matrix (GRM)

Environment effects included as fixed or random

G×E modeled via interaction terms or Kronecker covariance structures

2. Optional ML Ensemble
PCA of marker matrix

Gradient boosting model (XGBoost/LightGBM)

Weighted ensemble with GBLUP predictions

3. CV0 and CV00 Implementation
CV0: Exclude focal trial only

CV00: Exclude focal trial + all accessions appearing in that trial

Both follow the definitions from Jarquín et al. (2017).

Running the Full Pipeline
To generate predictions and submission files:

Code
python src/main.py
This will create:

Code
submission_output/
    ├── AWY1_DVPWA_2024/
    │   ├── CV0_Predictions.csv
    │   ├── CV0_Trials.csv
    │   ├── CV0_Accessions.csv
    │   ├── CV00_Predictions.csv
    │   ├── CV00_Trials.csv
    │   └── CV00_Accessions.csv
    ├── TCAP_2025_MANKS/
    └── ...
All files follow the exact formatting required by the competition.

submission_output/
├── AWY1_DVPWA_2024/
│   ├── CV0/
│   │   ├── CV0accessions.csv
│   │   ├── CV0trials.csv
│   │   └── CV0predictions.csv
│   └── CV00/
│       ├── CV00accessions.csv
│       ├── CV00trials.csv
│       └── CV00predictions.csv
├── TCAP_2025_MANKS/
└── ...

Focal Trials
The nine focal trials used in the challenge are:

AWY1_DVPWA_2024

TCAP_2025_MANKS

25_Big6_SVREC_SVREC

OHRWW_2025_SPO

CornellMaster_2025_McGowan

24Crk_AY2-3

2025_AYT_Aurora

YT_Urb_25

STP1_2025_MCG

References
Jarquín, D., Lemes da Silva, C., Gaynor, R.C., Poland, J., Fritz, A., et al. (2017).
Increasing genomic-enabled prediction accuracy by modeling genotype × environment interactions in Kansas wheat.  
Plant Genome, 10(2). doi: 10.3835/plantgenome2016.12.0130.

Methods Document
A draft of the required methods description for submission is located in:

Code
methods/methods_description_draft.md
This includes:

Data retrieval method

BrAPI calls or GUI download details

GRM construction

Model training

CV0/CV00 implementation

Code repository link


Data engineering:

Model development:

Pipeline automation:

Documentation:

License
Specify your license here (MIT, Apache 2.0, etc.).

Quick Start
This section provides a minimal, copy‑paste‑ready workflow for running the entire genomic prediction pipeline — from raw data to final submission files — using either Snakemake or the provided shell wrapper.

Option 1: Run the Entire Pipeline with Snakemake
Snakemake handles preprocessing, modeling, and submission generation automatically.

Run everything
bash
snakemake -p -j1
Run only preprocessing
bash
snakemake preprocess -p -j1
Run only modeling + submission generation
bash
snakemake modeling -p -j1
Force a clean rebuild
bash
snakemake -p -j1 --forcerun preprocess modeling
Increase wait time for networked filesystems (optional)
bash
snakemake -p -j1 --latency-wait 30
Option 2: Use the run_pipeline.sh Wrapper Script
A convenient wrapper is included to clean, preprocess, model, and generate submission files in one command.

Run full pipeline
bash
bash run_pipeline.sh
Clean + run full pipeline
This removes all processed data, submission outputs, and Snakemake metadata before rebuilding.

bash
bash run_pipeline.sh --clean
What the script does
Optional cleaning (--clean)

Runs Snakemake preprocessing

Runs Snakemake modeling

Produces the full submission folder structure

Expected Output Structure
After running either method, you will see:

Code
submission_output/
├── AWY1_DVPWA_2024/
│   ├── CV0/
│   │   ├── CV0accessions.csv
│   │   ├── CV0trials.csv
│   │   └── CV0predictions.csv
│   └── CV00/
│       ├── CV00accessions.csv
│       ├── CV00trials.csv
│       └── CV00predictions.csv
├── TCAP_2025_MANKS/
└── ...
