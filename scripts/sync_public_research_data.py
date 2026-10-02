from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "web" / "public" / "data"


INDEX_FILES = (
    "a_share_index_price_returns.csv",
    "etf_proxy_returns.csv",
    "index_catalog.csv",
    "index_api_probe.csv",
    "microcap/annual_returns.csv",
    "microcap/nav.csv",
    "microcap/reconstructed_daily_nav.csv",
    "microcap/reconstructed_summary.json",
    "microcap/reconstructed_underwater_periods.csv",
    "microcap/rolling_cagr.csv",
    "microcap/rolling_drawdown.csv",
    "microcap/source_notes.json",
    "microcap/summary.json",
    "cashflow_indices/cashflow_data_status.csv",
    "cashflow_indices/cashflow_performance.csv",
    "cashflow_indices/cashflow_rebalance_frequency.csv",
    "linked_indices/etf_index_pairing.csv",
    "linked_indices/linked_index_catalog.csv",
    "linked_indices/linked_index_fetch_status.csv",
    "linked_indices/paired_index_etf_representatives.csv",
    "linked_indices/paired_index_etf_returns_all.csv",
    "linked_indices/ten_year_price_returns.csv",
)


def copy_files(source_root: Path, target_root: Path, files: tuple[str, ...]) -> int:
    # Missing snapshots must fail before any existing public file is replaced.
    for relative in files:
        source = source_root / relative
        if not source.is_file():
            raise FileNotFoundError(source)
    copied = 0
    for relative in files:
        source = source_root / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        target = target_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied += 1
    return copied


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Migrate reviewed derived index snapshots; not a refresh job."
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        required=True,
        help="Directory containing reviewed public index outputs.",
    )
    parser.add_argument(
        "--target-root",
        type=Path,
        default=TARGET,
        help="Public snapshot directory containing manifest.json.",
    )
    args = parser.parse_args(argv)
    source_root = args.source_root.expanduser().resolve()
    target_root = args.target_root.expanduser().resolve()
    if source_root == (target_root / "index").resolve():
        raise SystemExit("source and destination must differ")
    manifest_path = target_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("included_snapshots"), dict):
        raise SystemExit("manifest must contain an included_snapshots object")
    copied = copy_files(source_root, target_root / "index", INDEX_FILES)
    manifest["included_snapshots"].update(index_research_files=copied, raw_data_published=False)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"copied {copied} derived public snapshot files into {target_root}")


if __name__ == "__main__":
    main()
