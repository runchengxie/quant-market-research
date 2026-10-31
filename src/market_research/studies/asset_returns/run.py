"""Run the asset-return study on explicit, frozen, verified monthly inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import gettempdir

import pandas as pd
import numpy as np

from .analysis import (
    cash_paths, diversification, earnings_attribution, holding_periods,
    monthly_mix, relative_premium, return_sources, validate_levels,
)


def run_study(input_path: Path, metadata_path: Path, output: Path) -> dict:
    output = output.resolve()
    if any((p / '.git').exists() for p in [output, *output.parents]
           if p != Path(gettempdir())):
        raise ValueError('run outputs must remain outside source repositories')
    if output.exists():
        raise FileExistsError('select a new output directory')
    input_bytes, metadata_bytes = input_path.read_bytes(), metadata_path.read_bytes()
    metadata = json.loads(metadata_bytes)
    if metadata.get('schema_version') != 1:
        raise ValueError('metadata schema_version must be 1')
    data = pd.read_csv(input_path)
    series = metadata.get('series', {})
    if not {'date', 'price', 'total'} <= set(data.columns):
        raise ValueError('date, price and total are required')
    currencies = set()
    for col in set(data.columns) - {'date'}:
        spec = series.get(col, {})
        if spec.get('coverage_verified') is not True or not spec.get('source_id'):
            raise ValueError(f'{col} requires source identity and verified coverage')
        if not spec.get('return_basis') or not spec.get('currency'):
            raise ValueError(f'{col} requires return basis and currency')
        if col not in {'cpi', 'pe'}:
            currencies.add(spec['currency'])
    if len(currencies) != 1:
        raise ValueError('convert all financial levels to one currency before running')
    if series['price']['return_basis'] != 'price' or series['total']['return_basis'] != 'total_return':
        raise ValueError('price and total must have their stated return bases')
    validate_levels(data, ['price', 'total'])
    result = {
        'schema_version': 1, 'evidence_stage': 'descriptive_history',
        'provenance': {'input_sha256': hashlib.sha256(input_bytes).hexdigest(),
                       'metadata_sha256': hashlib.sha256(metadata_bytes).hexdigest(),
                       'generated_at': datetime.now(timezone.utc).isoformat(),
                       'source_revision': metadata.get('source_revision'),
                       'series': series},
        'sources': return_sources(data), 'holding_periods': holding_periods(data),
        'limitations': ['Monthly sampling misses intramonth drawdowns and recoveries.',
                        'Historical revisions and index backfills are not point-in-time observations.',
                        'Overlapping windows are not independent; no significance claim.',
                        'Index distribution residual is not cash received.'],
    }
    if 'pe' in data:
        result['earnings_attribution'] = earnings_attribution(data)
    if 'benchmark' in data:
        if series['benchmark']['return_basis'] != 'total_return':
            raise ValueError('relative total-return comparison requires a total-return benchmark')
        result['relative_premium'] = relative_premium(data, 'total', 'benchmark')
    assets = [c for c in ['total', 'gold', 'bond'] if c in data]
    if len(assets) > 1:
        if 'bond' in assets and series['bond']['return_basis'] != 'total_return':
            raise ValueError('bond comparison requires a wealth/total-return series')
        result['diversification'] = diversification(data, assets, 'total')
        weights = {a: 1 / len(assets) for a in assets}
        result['equal_weight_sensitivities'] = [monthly_mix(data, weights, drag)
                                               for drag in [0, .005, .01]]
    paths = {}
    if 'cash_per_unit' in data:
        if metadata.get('cash_timing') != 'same_month_entitlement_and_payment':
            raise ValueError('cash scenarios require explicit same-month timing assumption')
        for name, kw in [('cash_retained', {}), ('fixed_4pct_initial_annual', {'fixed_withdrawal': .04 / 12}),
                         ('proportional_4pct_annual', {'withdrawal_rate': 1 - .96 ** (1 / 12)})]:
            paths[name] = cash_paths(data, **kw)
        result['cash_scenarios'] = {k: v.iloc[-1].to_dict() for k, v in paths.items()}
    # Validate serialization and every analysis before creating any output.
    serialized = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False, default=lambda value: value.item() if isinstance(value, np.generic) else str(value))
    output.mkdir(parents=True, exist_ok=False)
    (output / 'results.json').write_text(serialized + '\n')
    for name, path in paths.items():
        path.to_csv(output / (name + '.csv'), index=False)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run_study(args.input, args.metadata, args.output)
    print(json.dumps({'evidence_stage': result['evidence_stage'], 'sources': result['sources']}))


if __name__ == '__main__':
    main()
