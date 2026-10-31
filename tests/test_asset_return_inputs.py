import pandas as pd
import pytest


def test_monthly_endpoints_require_actual_last_session_quotes():
    from market_research.studies.asset_returns.inputs import month_end_levels
    cal = pd.to_datetime(['2025-01-30', '2025-01-31', '2025-02-27', '2025-02-28'])
    daily = pd.DataFrame({'date': cal, 'close': [99, 100, 101, 102]})
    result = month_end_levels(daily, cal)
    assert result.close.tolist() == [100, 102]
    assert result.date.dt.strftime('%Y-%m-%d').tolist() == ['2025-01-31', '2025-02-28']
    with pytest.raises(ValueError):
        month_end_levels(daily.iloc[:-1], cal)
    with pytest.raises(ValueError):
        month_end_levels(pd.concat([daily, daily.iloc[[0]]]), cal)


def test_frozen_response_requires_hash_and_success(tmp_path):
    from market_research.studies.asset_returns.inputs import read_frozen_response
    path = tmp_path / 'raw.json'
    path.write_text('{"code":0,"data":{"fields":["x"],"items":[[1]]}}')
    with pytest.raises(ValueError):
        read_frozen_response(path, 'bad-hash')
