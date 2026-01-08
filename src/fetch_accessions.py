#!/usr/bin/env python3
"""
Fetch accessions for one or more T3/Wheat trials via BrAPI v2.

Usage:
    python3 fetch_accessions.py \
        --trials 9364 9365 9366 \
        --out data/processed/trial_accessions.csv
"""

import argparse
import requests
import sys
import time
import csv
from urllib.parse import urljoin


def get_json_with_pagination(base_url, endpoint, params=None, page_size=1000):
    """
    Generic BrAPI v2 pagination helper.
    Yields each page's 'result' object.
    """
    if params is None:
        params = {}

    page = 0
    while True:
        q = params.copy()
        q["page"] = page
        q["pageSize"] = page_size

        url = urljoin(base_url, endpoint)
        r = requests.get(url, params=q)
        if r.status_code != 200:
            raise RuntimeError(
                f"Request failed {r.status_code} for {url} with params {q}: {r.text[:500]}"
            )

        data = r.json()
        result = data.get("result", {})
        metadata = data.get("metadata", {})
        pagination = metadata.get("pagination", {})

        yield result

        total_pages = pagination.get("totalPages")
        if total_pages is None:
            # No pagination info; assume single page
            break

        page += 1
        if page >= total_pages:
            break

        # be gentle
        time.sleep(0.2)


def fetch_studies_for_trial(base_url, trial_id):
    """
    Return a list of studyDbId for a given trialDbId.
    """
    endpoint = "/brapi/v2/studies"
    params = {"trialDbId": str(trial_id)}

    studies = []
    for result in get_json_with_pagination(base_url, endpoint, params=params):
        for study in result.get("data", []):
            studies.append(study["studyDbId"])

    return studies


def fetch_accessions_for_study(base_url, study_id):
    """
    Return a set of (germplasmDbId, germplasmName) for a given studyDbId,
    using the observationunits endpoint.
    """
    endpoint = "/brapi/v2/observationunits"
    params = {"studyDbId": str(study_id)}

    accessions = set()
    for result in get_json_with_pagination(base_url, endpoint, params=params):
        for ou in result.get("data", []):
            g = ou.get("germplasm") or {}
            germplasm_dbid = g.get("germplasmDbId")
            germplasm_name = g.get("germplasmName")

            if germplasm_dbid or germplasm_name:
                accessions.add((germplasm_dbid, germplasm_name))

    return accessions


def fetch_accessions_for_trials(base_url, trial_ids):
    """
    Return a dict:
        {
          trialDbId: set((germplasmDbId, germplasmName), ...)
        }
    """
    trial_to_accessions = {}

    for trial_id in trial_ids:
        print(f"\n=== Trial {trial_id} ===")
        studies = fetch_studies_for_trial(base_url, trial_id)
        print(f"Found {len(studies)} studies in trial {trial_id}")

        trial_accessions = set()
        for sid in studies:
            print(f"  Fetching accessions for study {sid} ...")
            study_accessions = fetch_accessions_for_study(base_url, sid)
            print(f"    {len(study_accessions)} accessions from study {sid}")
            trial_accessions.update(study_accessions)

        print(f"Total unique accessions in trial {trial_id}: {len(trial_accessions)}")
        trial_to_accessions[trial_id] = trial_accessions

    return trial_to_accessions


def write_accessions_csv(trial_to_accessions, out_path):
    """
    Write a CSV with columns:
        trialDbId, germplasmDbId, germplasmName
    """
    rows = []
    for trial_id, accs in trial_to_accessions.items():
        for germplasm_dbid, germplasm_name in accs:
            rows.append({
                "trialDbId": trial_id,
                "germplasmDbId": germplasm_dbid,
                "germplasmName": germplasm_name,
            })

    # optional: de-duplicate globally
    unique_rows = { (r["trialDbId"], r["germplasmDbId"], r["germplasmName"]) : r
                    for r in rows }.values()

    fieldnames = ["trialDbId", "germplasmDbId", "germplasmName"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in unique_rows:
            writer.writerow(r)

    print(f"\nWrote {len(list(unique_rows))} unique rows to {out_path}")


def parse_args():
    p = argparse.ArgumentParser(
        description="Fetch accessions for T3/Wheat trials via BrAPI v2"
    )
    p.add_argument(
        "--trials",
        nargs="+",
        required=True,
        help="List of trialDbId values (e.g. 9364 9365 9366)",
    )
    p.add_argument(
        "--out",
        required=True,
        help="Output CSV path",
    )
    p.add_argument(
        "--base-url",
        default="https://wheat.triticeaetoolbox.org",
        help="Base URL for T3/Wheat (default: https://wheat.triticeaetoolbox.org)",
    )
    return p.parse_args()


def main():
    args = parse_args()
    base_url = args.base_url.rstrip("/")

    try:
        trial_to_accessions = fetch_accessions_for_trials(base_url, args.trials)
    except Exception as e:
        print(f"Error while fetching accessions: {e}", file=sys.stderr)
        sys.exit(1)

    write_accessions_csv(trial_to_accessions, args.out)


if __name__ == "__main__":
    main()