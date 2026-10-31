import json
from pathlib import Path

import pandas as pd
import pytest


def test_run_records_hashes_and_refuses_unverified_coverage(tmp_path):
    from market_research.studies.asset_returns.run import run_study
    input_path = tmp_path / 'monthly.csv'
    pd.DataFrame({'date': ['2025-01-31', '2025-02-28'], 'price': [100, 101],
                  'total': [100, 102]}).to_csv(input_path, index=False)
    metadata = tmp_path / 'metadata.json'
    meta = {'schema_version': 1, 'series': {c: {'currency': 'CNY',
        'return_basis': basis, 'source_id': 'fixture', 'coverage_verified': True}
        for c, basis in [('price', 'price'), ('total', 'total_return')]}}
    metadata.write_text(json.dumps(meta))
    output = tmp_path / 'out'
    r = run_study(input_path, metadata, output)
    assert r['sources']['total_cagr'] > r['sources']['price_cagr']
    assert len(r['provenance']['input_sha256']) == 64
    assert (output / 'results.json').exists()
    saved = json.loads((output / 'results.json').read_text())
    assert saved['holding_periods']['recovery_entries'][-1]['breakeven_date'] is None
    with pytest.raises(FileExistsError):
        run_study(input_path, metadata, output)
    meta['series']['total']['coverage_verified'] = False
    metadata.write_text(json.dumps(meta))
    with pytest.raises(ValueError):
        run_study(input_path, metadata, tmp_path / 'unverified')
    assert not (tmp_path / 'unverified').exists()


def test_runner_rejects_currency_mismatch_and_repository_outputs(tmp_path):
    from market_research.studies.asset_returns.run import run_study
    input_path = tmp_path / 'monthly.csv'
    pd.DataFrame({'date': ['2025-01-31', '2025-02-28'], 'price': [100, 101],
                  'total': [100, 102]}).to_csv(input_path, index=False)
    meta = {'schema_version': 1, 'series': {c: {'currency': currency,
        'return_basis': basis, 'source_id': 'fixture', 'coverage_verified': True}
        for c, currency, basis in [('price', 'CNY', 'price'), ('total', 'USD', 'total_return')]}}
    metadata = tmp_path / 'metadata.json'
    metadata.write_text(json.dumps(meta))
    with pytest.raises(ValueError):
        run_study(input_path, metadata, tmp_path / 'out')
    with pytest.raises(ValueError):
        run_study(input_path, metadata, Path(__file__).resolve().parents[1] / 'results-forbidden')
