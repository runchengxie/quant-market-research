#!/usr/bin/env python3
"""Compare frozen feature versions before replacing reviewed research evidence.

Exit 2 means historical changes require review; never updates a latest pointer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb

from market_research.liquidity_revision import compare_features


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ["baseline", "candidate", "output"]:
        p.add_argument("--" + k, type=Path, required=True)
    p.add_argument("--expected-baseline-sha256", required=True)
    a = p.parse_args()
    if sha(a.baseline) != a.expected_baseline_sha256:
        raise ValueError("baseline checksum differs from frozen receipt")
    if a.output.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("revision results must remain outside the repository")
    a.output.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.execute("SET memory_limit='2GB'")
    con.execute("SET temp_directory='" + str(a.output / "spill").replace("'", "''") + "'")
    for name, path in [("baseline", a.baseline), ("candidate", a.candidate)]:
        con.read_parquet(str(path)).create_view(name)
    result = compare_features(con, "baseline", "candidate")
    hashes = {k: sha(getattr(a, k)) for k in ["baseline", "candidate"]}
    result.update(
        schema_version="liquidity.feature-revision.v1",
        sha256=hashes,
        comparison_kind="same_bytes_baseline_only"
        if hashes["baseline"] == hashes["candidate"]
        else "distinct_input_bytes",
        longitudinal_vendor_stability_verified=False,
        scope="Exact full feature rows with identical schema; supplier raw partitions and minute reconciliation are separate checks.",
        baseline_policy="Retain the prior feature file immutably outside Git and pass it explicitly. Do not reuse a mutable latest alias as the baseline.",
    )
    (a.output / "revision-review.json").write_text(json.dumps(result, indent=2) + "\n")
    (a.output / "inputs.private.json").write_text(
        json.dumps({k: str(getattr(a, k).resolve()) for k in ["baseline", "candidate"]}, indent=2)
        + "\n"
    )
    print(json.dumps(result))
    raise SystemExit(2 if result["status"] == "review_required" else 0)


if __name__ == "__main__":
    main()
