import importlib.util
from pathlib import Path

import pandas as pd
import pytest


def module():
    spec = importlib.util.spec_from_file_location('regime_prepare',
        Path(__file__).parents[2] / 'scripts/prepare_execution_market_regimes.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def frames():
    base = pd.DataFrame({'ts_code': ['600001.SH'], 'trade_date': ['20240102'],
                         'close': [1.], 'amount': [100.]})
    raw = base.assign(down_limit=.9)
    return base, raw


def test_limits_bind_exact_price_and_amount_source():
    base, raw = frames()
    assert module().bind_market_limits(base, raw).down_limit.tolist() == [.9]
    raw.loc[0, 'close'] -= 1e-10
    with pytest.raises(AssertionError):
        module().bind_market_limits(base, raw)


def test_missing_or_duplicate_limit_rows_are_not_inferred():
    base, raw = frames()
    with pytest.raises(ValueError):
        module().bind_market_limits(base, raw.iloc[:0])
    with pytest.raises(ValueError):
        module().bind_market_limits(base, pd.concat([raw, raw]))
