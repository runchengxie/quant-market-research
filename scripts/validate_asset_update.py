"""Validate an append-only monthly update and bind reviewed inputs by SHA-256.

Writes an exclusive external receipt; does not publish data or move aliases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import gettempdir

import pandas as pd

from market_research.studies.asset_returns.release import validate_update


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("previous", "candidate", "previous-contract", "candidate-contract", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if any(
        (p / ".git").exists()
        for p in [out, *out.parents]
        if p not in {Path.home(), Path(gettempdir())}
    ):
        parser.error("receipts belong outside source repositories")
    paths = {
        "previous": args.previous,
        "candidate": args.candidate,
        "previous_contract": args.previous_contract,
        "candidate_contract": args.candidate_contract,
    }
    # Hash the same bytes parsed below, avoiding a read/hash race.
    import io

    blobs = {key: path.read_bytes() for key, path in paths.items()}
    result = validate_update(
        pd.read_csv(io.BytesIO(blobs["previous"])),
        pd.read_csv(io.BytesIO(blobs["candidate"])),
        json.loads(blobs["previous_contract"]),
        json.loads(blobs["candidate_contract"]),
    )
    result["schema_version"] = 1
    result["input_sha256"] = {key: hashlib.sha256(blob).hexdigest() for key, blob in blobs.items()}
    from market_research.studies.asset_returns import closure, release

    result["gate_code_sha256"] = {
        name: hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
        for name, module in [("closure", closure), ("release", release)]
    }
    with out.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
