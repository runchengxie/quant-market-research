"""Project reviewed closure aggregates; exclude raw security records and paths."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def project(source: Path, output: Path):
    blob = source.read_bytes()
    data = json.loads(blob)
    result = {
        "schema_version": 1,
        "source_result_sha256": hashlib.sha256(blob).hexdigest(),
        "cohorts": data["cohorts"],
        "etf_years": data["etf_years"],
        "sources": data["sources"],
        "code_sha256": data["code_sha256"],
        "income_sha256": data["income_sha256"],
        "scope": "Descriptive reconciliation; original financial vintages, corporate-action continuity and complete ETF attribution remain unresolved.",
    }
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project(args.source, args.output)
