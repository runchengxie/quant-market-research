"""Explicit public aggregate projection of the four reviewed asset-return runs.

No daily/monthly level history, row-level financials or machine paths are copied.
Review the result and provenance before committing the projection to the site.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def project(runs: Path) -> dict:
    studies = {name: json.loads((runs / name / 'results.json').read_text())
               for name in ['all_share', 'large_cap', 'small_cap', 'multi_asset']}
    if any(s['evidence_stage'] != 'descriptive_history' for s in studies.values()):
        raise ValueError('only descriptive-history runs are supported')
    result = {'schema_version': 1, 'as_of': '2025-12-31', 'retrieved': '2026-10-31',
              'frequency': 'monthly', 'currency': 'CNY', 'equities': [],
              'evidence_stage': 'descriptive_history', 'provenance': {}}
    for name, s in studies.items():
        provenance = s['provenance']
        result['provenance'][name] = {
            key: provenance[key] for key in ['input_sha256', 'metadata_sha256',
                                             'analysis_sha256', 'runner_sha256']}
        result['provenance'][name]['result_sha256'] = hashlib.sha256((runs / name / 'results.json').read_bytes()).hexdigest()
        if name == 'multi_asset':
            continue
        source = s['sources']
        result['equities'].append({
            'id': name, 'start': '2004-12-31', 'end': '2025-12-31',
            'months': source['months'],
            **{k: source[k] for k in ['price_cagr', 'total_cagr', 'distribution_component_cagr']},
            'horizons': s['holding_periods']['horizons'],
        })
    multi = studies['multi_asset']
    result['diversification'] = {
        'start': '2007-01-31', 'end': '2025-12-31',
        'months': multi['diversification']['observations'],
        'correlation': multi['diversification']['correlation'],
        'down_market': multi['diversification']['down_market'],
        'mix_sensitivities': multi['equal_weight_sensitivities'],
    }
    small = studies['small_cap']
    result['small_vs_large'] = {
        'start': '2004-12-31', 'end': '2025-12-31',
        'relative_cagr': small['relative_premium']['relative_cagr'],
        'relative_max_drawdown': small['relative_premium']['relative_max_drawdown'],
        'cost_sensitivities': [{k: row[k] for k in ['annual_wealth_drag', 'relative_cagr',
                                                 'calibrated_execution_cost']}
                               for row in small['relative_cost_sensitivities']],
    }
    # Future result fields cannot leak through an unrestricted object spread.
    json.dumps(result, allow_nan=False)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('review existing projection before replacing it')
    args.output.write_text(json.dumps(project(args.runs), ensure_ascii=False, indent=2) + '\n')
