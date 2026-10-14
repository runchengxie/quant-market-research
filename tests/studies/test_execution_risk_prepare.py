import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    'risk_prepare', Path(__file__).parents[2] / 'scripts/prepare_execution_risk_comparison.py')


def load():
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_source_verification_ignores_unconsumed_current_metadata_only(tmp_path):
    module = load()
    leaf = tmp_path / 'leaf'
    leaf.write_text('original')
    expected = {'daily': module.sha(leaf), 'current': 'old-current'}
    assert module.verify_source_leaves({'daily': leaf}, expected) == {'daily': module.sha(leaf)}
    leaf.write_text('changed')
    with pytest.raises(ValueError, match='daily'):
        module.verify_source_leaves({'daily': leaf}, expected)


def test_prepared_parent_hashes_reject_tampering_and_path_escape(tmp_path):
    module = load()
    leaf = tmp_path / 'bars.parquet'
    leaf.write_text('original')
    module.verify_parent_inputs(tmp_path, {'bars.parquet': module.sha(leaf)})
    leaf.write_text('changed')
    with pytest.raises(ValueError, match='bars.parquet'):
        module.verify_parent_inputs(tmp_path, {'bars.parquet': 'original-hash'})
    with pytest.raises(ValueError, match='filename'):
        module.verify_parent_inputs(tmp_path, {'../outside': 'x'})


@pytest.mark.parametrize('kind', ['same', 'nested', 'parent', 'original'])
def test_output_paths_reject_overlap(tmp_path, kind):
    module = load()
    original = tmp_path / 'original'
    left = tmp_path / 'baseline'
    right = {'same': left, 'nested': left / 'risk', 'parent': tmp_path,
             'original': original}[kind]
    with pytest.raises(ValueError, match='distinct'):
        module.validate_output_paths(original, [left, right])


def test_risk_selection_must_fit_immutable_execution_scope():
    module = load()
    with pytest.raises(ValueError, match='outside original scope'):
        module.validate_selected_symbols({'000001.SZ', '000002.SZ'}, {'000001.SZ'})
    module.validate_selected_symbols({'000001.SZ'}, {'000001.SZ', '000002.SZ'})


def test_selected_panel_changes_reject_even_with_unchanged_manifest():
    import pandas as pd

    module = load()
    original = pd.DataFrame({'trade_date': ['20240102'], 'ts_code': ['000001.SZ'],
                             'close': [2.]})
    full = pd.concat([original, pd.DataFrame({'trade_date': ['20240102'],
                     'ts_code': ['000002.SZ'], 'close': [3.]})], ignore_index=True)
    module.verify_selected_panel(full, original, {'000001.SZ'})
    full.loc[full.ts_code.eq('000001.SZ'), 'close'] = 2. + 1e-10
    with pytest.raises(AssertionError):
        module.verify_selected_panel(full, original, {'000001.SZ'})


def test_retained_full_panel_tampering_rejects(tmp_path):
    import pandas as pd

    module = load()
    path = tmp_path / 'full-selection-panel.parquet'
    pd.DataFrame({'close': [2.]}).to_parquet(path)
    hashes = {path.name: module.sha(path)}
    module.verify_parent_inputs(tmp_path, hashes)
    pd.DataFrame({'close': [3.]}).to_parquet(path)
    with pytest.raises(ValueError, match='full-selection-panel'):
        module.verify_parent_inputs(tmp_path, hashes)
