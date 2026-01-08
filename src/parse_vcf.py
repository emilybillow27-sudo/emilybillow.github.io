# src/parse_vcf.py

import argparse
from vcf_utils import parse_vcf_to_dosage

def main():
    parser = argparse.ArgumentParser(description="Convert VCF to dosage matrix")
    parser.add_argument("--vcf", required=True, help="Path to VCF file")
    parser.add_argument("--out", required=True, help="Output CSV path")
    args = parser.parse_args()

    parse_vcf_to_dosage(args.vcf, args.out)

if __name__ == "__main__":
    main()
