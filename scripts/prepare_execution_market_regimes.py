"""Bind actual daily price limits to a frozen full-universe selection panel."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import pandas as pd


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(part)
    return value.hexdigest()


def bind_market_limits(selection, raw):
    keys = ['ts_code', 'trade_date']
    fields = [*keys, 'close', 'amount']
    if raw.duplicated(keys).any() or selection.duplicated(keys).any() or len(raw) != len(selection):
        raise ValueError('incomplete or duplicate market limit coverage')
    pd.testing.assert_frame_equal(
        selection[fields].sort_values(keys).reset_index(drop=True),
        raw[fields].sort_values(keys).reset_index(drop=True), check_exact=True)
    return selection[fields].merge(raw[[*keys, 'down_limit']], on=keys, validate='one_to_one')


def prepare(prepared, output):
    root, output = Path(prepared), Path(output)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('market regime output must be new or empty')
    inputs = json.loads((root / 'inputs.json').read_text())
    panel_path = root / 'full-selection-panel.parquet'
    if sha(panel_path) != inputs['input_sha256'][panel_path.name]:
        raise ValueError('selection panel hash mismatch')
    refs = inputs['experiment_study']['source_refs']
    daily = next(ref for ref in refs if ref['name'] == 'daily')
    manifest = Path(daily['path'])
    if sha(manifest) != daily['sha256']:
        raise ValueError('daily manifest hash mismatch')
    with duckdb.connect() as con:
        con.execute("SET memory_limit='2GB'")
        con.execute('SET threads=2')
        raw = con.execute('SELECT ts_code,trade_date,close,amount,down_limit FROM read_parquet(?) '
                          'WHERE trade_date BETWEEN ? AND ?',
                          [str(manifest.parent / 'data/*.parquet'), inputs['start'], inputs['end']]).df()
    raw['trade_date'] = raw.trade_date.astype(str)
    panel = pd.read_parquet(panel_path)
    result = bind_market_limits(panel, raw)
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'market-regime-panel.parquet'
    result.to_parquet(path, index=False)
    receipt = dict(schema='execution-market-regime-inputs.v1', source_manifest_sha256=daily['sha256'],
                   selection_panel_sha256=sha(panel_path), rows=len(result),
                   input_sha256={path.name: sha(path)}, price_amount_exact_selection_panel=True,
                   implementation_sha256=sha(Path(__file__)), revision_safe=False,
                   limitation='Current daily snapshot, not proof of historical unselected-row revisions')
    (output / 'inputs.json').write_text(json.dumps(receipt, indent=2, allow_nan=False)+'\n')
    print('bound market regime rows', len(result), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.prepared, args.output)


if __name__ == '__main__':
    main()
