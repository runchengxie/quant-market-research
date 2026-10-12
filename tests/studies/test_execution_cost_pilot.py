import numpy as np
import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.pilot import (
    book_metrics, clock_minutes, earliest_per_minute, walk_notional,
)


def test_clock_rejects_alias_milliseconds_and_session_endpoints():
    clock = clock_minutes(np.array([93000000, 113000000, 130000000, 145659999, 145700000, -900000]))
    assert clock.tolist() == [570, -1, 780, 896, -1, -1]


def test_sampling_keeps_earliest_timestamp_and_stable_source_tie():
    rows = pd.DataFrame({'SecuCode': [1, 1, 1], 'TradingDay': [20260424]*3,
                         'TickTime': [93003000, 93000000, 93100000], 'minute': [570,570,571],
                         'source_row': [5,6,7]})
    assert earliest_per_minute(rows)['source_row'].tolist() == [6,7]


def test_symmetric_walk_contains_half_spread_and_depth_only_once():
    bid = np.array([[9.99, 9.98]])
    ask = np.array([[10.01, 10.02]])
    qty = np.array([[100., 100.]])
    metrics = book_metrics(bid, ask, qty, qty)
    assert metrics['valid'].tolist() == [True]
    assert metrics['spread_bp'][0] == pytest.approx(20)
    buy = walk_notional(ask, qty, metrics['mid'], 1500, 'buy')
    sell = walk_notional(bid, qty, metrics['mid'], 1500, 'sell')
    assert buy['cost_bp'][0] == pytest.approx(13.3333333333)
    assert sell['cost_bp'][0] == pytest.approx(13.3333333333)


def test_incomplete_depth_never_returns_full_order_cost():
    result = walk_notional(np.array([[10.01, 0.]]), np.array([[100., 0.]]),
                           np.array([10.]), 2000, 'buy')
    assert result['coverage'][0] == pytest.approx(.5)
    assert np.isnan(result['cost_bp'][0])
    assert result['covered_cost_bp'][0] == pytest.approx(10)


def test_one_sided_crossed_nonfinite_and_gapped_books_are_excluded():
    bid = np.array([[0,0], [10.02,10.01], [9.99,9.98], [9.99,0], [9.99,9.98]])
    ask = np.array([[10.01,10.02], [10.01,10.02], [10.02,10.01], [10.01,10.02], [10.01,10.02]])
    bq = np.array([[0,0],[100,100],[100,100],[100,100],[100,np.nan]])
    aq = np.full((5,2),100.)
    assert not book_metrics(bid,ask,bq,aq)['valid'].any()


def test_invalid_budget_is_rejected():
    with pytest.raises(ValueError):
        walk_notional(np.array([[10.]]),np.array([[100.]]),np.array([10.]),0,'buy')


def test_summary_exposes_same_population_comparison_for_large_orders():
    from market_research.studies.ashare_execution_costs.pilot import summarize, SIZES
    frame = pd.DataFrame({'TradingDay':[20260424,20260424], 'SecuCode':[1,2],
                          'spread_bp':[2,20], 'bid_depth_cny':[10000000,10000],
                          'ask_depth_cny':[10000000,10000]})
    for side in ['buy','sell']:
        for size in SIZES:
            frame[f'{side}_{size}_cost_bp'] = [size/10000, 10 if size==10000 else np.nan]
            frame[f'{side}_{size}_coverage'] = [1,1 if size==10000 else .1]
    result = summarize(frame)
    assert result['common_full_subset']['snapshots'] == 1
    assert result['common_full_subset']['cost_surface'][0]['full_order_cost_bp']['p50'] == 1


def test_sample_source_refuses_renamed_relative_clock(tmp_path, monkeypatch):
    import sys
    import types
    import pyarrow as pa
    import pyarrow.parquet as pq
    from market_research.studies.ashare_execution_costs.pilot import sample_source

    # Fixture provider keeps this test independent of a separate repository install.
    provider = types.ModuleType('quant_market_data_platform.l2_views')
    provider.iter_l2_batches = lambda *args, **kwargs: iter(())
    monkeypatch.setitem(sys.modules, 'quant_market_data_platform.l2_views', provider)
    path = tmp_path / 'relative-clock.parquet'
    pq.write_table(pa.table({'ticker':['000037'], 'time_ms':[0]}),path)
    with pytest.raises(ValueError, match='aliases need audit'):
        sample_source(path,20260424,37,65536)
