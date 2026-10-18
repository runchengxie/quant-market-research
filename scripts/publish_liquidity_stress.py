#!/usr/bin/env python3
"""Copy only exact independently reviewed aggregate bytes into a public asset."""

import argparse
import json
from pathlib import Path

from market_research.liquidity_stress_publication import reviewed_stress


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["proposal", "review", "base", "output"]:
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    raw = a.proposal.read_bytes()
    reviewed_stress(raw, json.loads(a.review.read_text()), json.loads(a.base.read_text()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = a.output.with_suffix(".tmp")
    temporary.write_bytes(raw)
    temporary.replace(a.output)


if __name__ == "__main__":
    main()
