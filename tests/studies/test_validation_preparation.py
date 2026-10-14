import importlib.util
from pathlib import Path

import pandas as pd
import pytest


def module():
    spec = importlib.util.spec_from_file_location(
        'validation_prepare', Path(__file__).parents[2] / 'scripts/prepare_execution_validation_suite.py')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_modes_do_not_silently_claim_2025_announcement_coverage():
    m = module()
    assert m.mode_flags('price_st') == (True, True, False)
    assert m.mode_flags('baseline') == (False, False, False)
    with pytest.raises(ValueError):
        m.mode_flags('unknown')


def test_selected_input_identity_is_exact_even_when_rank_unchanged():
    m = module()
    panel = pd.DataFrame({'ts_code': ['600001.SH'], 'trade_date': ['20240102'], 'close': [1.]})
    revised = panel.copy()
    revised.loc[0, 'close'] -= 1e-10
    with pytest.raises(AssertionError):
        m.verify_selected_panel(revised, panel, {'600001.SH'})


def test_equal_targets_use_immutable_parent_bytes(tmp_path):
    m = module()
    frame = pd.DataFrame({'symbol': ['600001.SH'], 'weight': [.025]})
    source = tmp_path / 'source.parquet'
    output = tmp_path / 'new.parquet'
    frame.to_parquet(source, index=False)
    assert m.freeze_targets(frame, source, output) is True
    assert output.stat().st_ino == source.stat().st_ino
    assert m.sha(output) == m.sha(source)


def test_changed_targets_cannot_mutate_parent(tmp_path):
    m = module()
    frame = pd.DataFrame({'symbol': ['600001.SH'], 'weight': [.025]})
    source = tmp_path / 'source.parquet'
    output = tmp_path / 'new.parquet'
    frame.to_parquet(source, index=False)
    before = m.sha(source)
    frame.loc[0, 'symbol'] = '600002.SH'
    assert m.freeze_targets(frame, source, output) is False
    assert m.sha(source) == before
    assert output.stat().st_ino != source.stat().st_ino
