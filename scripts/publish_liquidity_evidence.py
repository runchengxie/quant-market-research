#!/usr/bin/env python3
"""Publish only independently reviewed aggregate bytes, retaining exact checksums."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from market_research.liquidity_publication import reviewed_publication
from market_research.liquidity_revision import validate_replacement


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--revision-review",
        type=Path,
        help="Required when replacing the published SH/SZ feature version",
    )
    args = parser.parse_args()
    raw = args.proposal.read_bytes()
    proposed = reviewed_publication(raw, json.loads(args.review.read_text()))
    if args.output.is_file():
        report = json.loads(args.revision_review.read_text()) if args.revision_review else None
        validate_replacement(json.loads(args.output.read_text()), proposed, report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".json.tmp")
    temporary.write_bytes(raw)
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
