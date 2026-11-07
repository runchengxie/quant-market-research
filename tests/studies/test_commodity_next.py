import numpy as np
import pandas as pd
import pytest

from market_research.studies.commodity_equity.risk_controls import lagged_risk_control
from market_research.studies.commodity_equity.contract_trial import settlement_trial


def test_risk_weights_do_not_use_future_prices():
    dates = pd.bdate_range('2010-01-01', periods=850)
    rng = np.random.default_rng(3)
    panel = pd.DataFrame(np.exp(np.cumsum(rng.normal(0, .01, (850, 2)), axis=0)), index=dates, columns=['equity', 'commodity'])
    ends = pd.DatetimeIndex(pd.Series(dates, index=dates.to_period('M')).groupby(level=0).max())
    first = lagged_risk_control(panel, ends, lookback=60)
    changed = panel.copy()
    changed.loc[dates[500]:, 'commodity'] *= 20
    second = lagged_risk_control(changed, ends, lookback=60)
    pd.testing.assert_series_equal(first['weights'].loc[:dates[499]], second['weights'].loc[:dates[499]])
    assert first['weights'].between(0, 1).all()
    assert first['nav'].iloc[0] == 1


def trial_input():
    dates = pd.bdate_range('2025-01-01', periods=4)
    rows = []
    for d in dates:
        for code, price in [('A', 100 + dates.get_loc(d)), ('B', 200 + dates.get_loc(d))]:
            rows.append(dict(trade_date=d, ts_code=code, settle=price, trading_fee=1.5, long_margin_rate=.1, vol=1000))
    return pd.DataFrame(rows), dates


def test_contract_roll_does_not_create_price_gap_profit_and_charges_both_legs():
    frame, dates = trial_input()
    result = settlement_trial(frame, [(dates[1], 'A'), (dates[2], 'B')], dates[3], capital=10000, per_unit=10, slippage_ticks=0)
    ledger = result['ledger']
    assert ledger[0]['lots'] == 10
    assert ledger[1]['lots'] == 4  # quantity sized at prior B settlement, with fee-funded equity
    assert ledger[1]['pnl'] == 100
    assert ledger[1]['traded_lots'] == 14
    assert ledger[1]['fee'] == 21
    assert ledger[-1]['lots'] == 0
    assert ledger[-1]['fee'] == 6
    assert result['total_pnl'] == 140
    assert result['terminal_equity'] == 10000 + 140 - 42


def test_contract_missing_mark_or_margin_fails_closed():
    frame, dates = trial_input()
    frame.loc[frame.trade_date == dates[2], 'long_margin_rate'] = 2
    with pytest.raises(ValueError, match='margin'):
        settlement_trial(frame, [(dates[1], 'A')], dates[3], capital=10000, per_unit=10)
