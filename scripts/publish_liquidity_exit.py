#!/usr/bin/env python3
"""Publish exact reviewed exit aggregates and bounded companion audit summaries."""

import argparse
import json
from pathlib import Path

from market_research.liquidity_exit_publication import reviewed_exit, validate_public_payload


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["run", "base", "output"]:
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    raw = (a.run / "summary.proposed.json").read_bytes()
    review = json.loads((a.run / "independent-review.json").read_text())
    evidence = reviewed_exit(raw, review, json.loads(a.base.read_text()))
    minute = json.loads((a.run / "minute-probe/minute-probe.json").read_text())
    revision = json.loads((a.run / "revision-baseline/revision-review.json").read_text())
    for other in [minute, revision]:
        validate_public_payload(other)
    if (
        minute["feature_sha256"] != evidence["feature_sha256"]
        or not minute["reviewed"]
        or minute["native_interval_semantics_verified"] is not False
    ):
        raise ValueError("minute scope or evidence declaration differs")
    if (
        sum(r["accepted"] for r in minute["quality"]) != minute["accepted_stock_days"]
        or len(minute["quality"]) != minute["dates"]
    ):
        raise ValueError("minute sample ledger does not conserve observations")
    if (
        revision["sha256"]["baseline"] != evidence["feature_sha256"]
        or revision["longitudinal_vendor_stability_verified"] is not False
    ):
        raise ValueError("revision baseline scope differs")
    a.output.mkdir(parents=True, exist_ok=True)
    payloads = {
        "exit-exploration.json": raw,
        "exit-review.json": (a.run / "independent-review.json").read_bytes(),
        "minute-clock-probe.json": (a.run / "minute-probe/minute-probe.json").read_bytes(),
        "revision-baseline.json": (a.run / "revision-baseline/revision-review.json").read_bytes(),
    }
    for name, value in payloads.items():
        path = a.output / name
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(value)
        temporary.replace(path)


if __name__ == "__main__":
    main()
