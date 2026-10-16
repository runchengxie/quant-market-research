"""Export explicitly reviewed aggregates, without running a backtest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from market_research.microcap_review import project_retained_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = project_retained_bundle(args.source)
    # Exclusive creation prevents overwriting an earlier review or a shared asset.
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"output": str(args.output), "buffer_rows": len(result["buffer_matrix"]), "era_rows": len(result["era_summary"]), "regime_rows": len(result["regime_summary"]), "capacity_rows": len(result["capacity_matrix"])}))


if __name__ == "__main__":
    main()
