import json

import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.analysis_summary import (
    compare_reports,
    market_regime_summary,
)


def report(symbols):
    pnl = sum(x['pnl'] for x in symbols.values())
    return dict(initial_capital=1000, final_nav=1000+pnl, pnl=pnl, symbols=symbols)


def test_pair_dividends_fees_and_identity():
    baseline = report({'600321.SH': dict(pnl=-11, fees=1), '002621.SZ': dict(pnl=4, fees=2), 'A': dict(pnl=12, fees=3)})
    risk = report({'002621.SZ': dict(pnl=7, fees=1), 'B': dict(pnl=20, fees=2)})
    r = compare_reports(baseline, risk)
    assert r['buckets']['avoided_two_gross_pnl_delta'] == 10
    assert r['buckets']['retained_002621_gross_pnl_delta'] == 2
    assert r['buckets']['other_replacement_rebalancing_gross_pnl_delta'] == 7
    assert r['buckets']['fee_pnl_delta'] == 3
    assert r['nav_profit_delta'] == 22
    assert r['identity_residual'] == 0
    json.dumps(r, allow_nan=False)
    risk['final_nav'] += 1
    with pytest.raises(ValueError, match='identity'):
        compare_reports(baseline, risk)


def frames(n=30):
    dates = pd.bdate_range('2024-01-01', periods=n)
    full = pd.DataFrame(dict(ts_code=['600001.SH']*n, trade_date=dates, amount=[100]*n, close=[10]*n, down_limit=[9]*n))
    daily = pd.DataFrame(dict(date=dates, nav=[1000+i for i in range(n)], transaction_cost=range(n)))
    return full, daily


def test_future_invariance_history_and_prior_stress():
    full, daily = frames()
    full.loc[22, 'close'] = 9
    full.loc[18:22, 'amount'] = 1
    r = market_regime_summary(full, daily)
    sessions = r['sessions']
    assert all(x['history_status'] == 'insufficient_history' for x in sessions[:20])
    assert not sessions[22]['down_limit_stress']
    assert sessions[23]['down_limit_stress']
    assert sessions[23]['low_liquidity']
    more, more_daily = frames(35)
    more.loc[:29] = full.values
    past = market_regime_summary(more, more_daily)['sessions'][:30]
    assert past == sessions


def test_missing_limit_data_is_unavailable_and_first_cost_counted():
    full, daily = frames()
    full = full.drop(columns='down_limit')
    daily['transaction_cost'] += 5
    r = market_regime_summary(full, daily)
    assert r['sessions'][20]['down_limit_stress'] is None
    assert sum(x['transaction_cost_delta'] for x in r['regimes'].values()) == 34
