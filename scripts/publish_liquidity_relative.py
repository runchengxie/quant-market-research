#!/usr/bin/env python3
"""Publish exact independently reviewed relative aggregate bytes, bound to base."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from market_research.liquidity_relative_publication import reviewed_relative


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["proposal", "review", "base", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    raw = args.proposal.read_bytes()
    reviewed_relative(raw, json.loads(args.review.read_text()), args.base.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".json.tmp")
    temporary.write_bytes(raw)
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
