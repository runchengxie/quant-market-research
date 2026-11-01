"""Project reviewed decision-risk aggregates; never include per-window inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

KEYS = [
    "schema_version",
    "sample",
    "uncertainty",
    "eras",
    "spending",
    "stress",
    "events",
    "launches",
    "products",
    "conclusion_register",
    "availability",
    "provenance",
    "scope",
]


def project(source: Path, output: Path) -> dict:
    blob = source.read_bytes()
    full = json.loads(blob)
    result = {key: full[key] for key in KEYS}
    result["source_result_sha256"] = hashlib.sha256(blob).hexdigest()
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project(args.source, args.output)
