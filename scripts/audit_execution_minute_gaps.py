#!/usr/bin/env python3
"""Audit saved security-minute selection keys and export only venue aggregates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from market_research.execution_minute_gaps import summarize_minute_gaps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = dict(schema_version="execution.sample-minute-gaps.v1", days=[])
    for path in args.selection:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        data = summarize_minute_gaps(
            pd.read_parquet(path, columns=["SecuCode", "minute"]),
            list(range(570, 690)) + list(range(780, 897)),
        )
        data.update(day=path.stem.rsplit("-", 1)[-1], selection_sha256=digest)
        result["days"].append(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
