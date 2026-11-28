"""Run the three-arm support diagnostic into a new external directory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from market_research.smallcap_target_support import build_target_support


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--panel', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output == repo or repo in output.parents:
        raise ValueError('outputs must be outside the source checkout')
    targets, support, metrics = build_target_support(pd.read_parquet(args.panel))
    output.mkdir(parents=True, exist_ok=False)
    targets.to_parquet(output / 'targets.private.parquet', index=False)
    support.to_csv(output / 'support.csv', index=False)
    metrics.to_csv(output / 'formation_metrics.csv', index=False)
    numeric = [c for c in metrics if c not in ['date', 'scope', 'arm']]
    grouped = metrics.groupby(['scope', 'arm'])[numeric]
    summary = grouped.mean().join(grouped.count().add_suffix('_valid_dates')).reset_index()
    summary.to_csv(output / 'summary.csv', index=False)
    manifest = {'schema': 'smallcap.target-support.v1', 'stage': 'archived_target_diagnostic',
                'input_sha256': sha(args.panel), 'runner_sha256': sha(Path(__file__)),
                'implementation_sha256': sha(repo / 'src/market_research/smallcap_target_support.py'),
                'input_formation_dates': support.date.nunique(),
                'supported_formation_dates': metrics.date.nunique(),
                'first_supported_date': metrics.date.min(), 'last_supported_date': metrics.date.max(),
                'pit_certified': False, 'returns_computed': False, 'execution_simulated': False,
                'cut_policy': 'ceil(20% of common finite-score support), ties ordered by symbol',
                'support_policy': 'cohort first; common finite raw low-turnover support for all arms',
                'target_change': 'half L1 of consecutive available source-date target weights; not realized turnover',
                'missing_policy': 'no descriptor renormalization; insufficient source dates reset transitions',
                'outputs': {p.name: sha(p) for p in sorted(output.iterdir())}}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
