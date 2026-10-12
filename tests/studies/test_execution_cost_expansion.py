import numpy as np
import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.expansion import (
    clock_ms, lagged_features, minute_coverage, reference_audit, stream_audit,
)


def test_clock_profiles_keep_lunch_and_preopening_and_reject_malformed_times():
    native = clock_ms(np.array([91500000, 93000000, 130000000, 150000000, 116000000]), 'native_hhmmssmmm')
    relative = clock_ms(np.array([-900000, 0, 12600000, 19800000]), 'relative_0930_ms')
    assert native[:4].tolist() == relative.tolist()
    assert np.isnan(native[-1])
    with pytest.raises(ValueError, match='clock profile'):
        clock_ms(np.array([0]), 'infer')


def test_minute_coverage_counts_missing_bins_without_filling_one_sided_books():
    rows = pd.DataFrame({'SecuCode': [1, 1, 2], 'minute': [570, 571, 570]})
    result = minute_coverage(rows, [1, 2, 3])
    assert result['expected_security_minutes'] == 3 * 237
    assert result['observed_security_minutes'] == 3
    assert result['missing_security_minutes'] == 3 * 237 - 3


def test_reference_audit_retains_ambiguous_and_missing_order_ids():
    orders = pd.DataFrame({'SecuCode': [1, 1, 1], 'OrderID': [10, 10, 20]})
    trades = pd.DataFrame({'SecuCode': [1, 1, 1], 'Price': [100, 100, 0], 'Volume': [10]*3,
                           'BuyID': [10, 30, 0], 'SellID': [20, 20, 0]})
    result = reference_audit(orders, trades, 'OrderID')
    assert result['eligible_positive_trade_rows'] == 2
    assert result['buy']['matched'] == 1
    assert result['buy']['ambiguous'] == 1
    assert result['buy']['missing'] == 1
    assert result['sell']['unique'] == 2
    assert result['identity_scope'] == 'security_only_channel_unavailable'


def test_channel_scope_prevents_false_reference_matches():
    orders = pd.DataFrame({'SecuCode': [1], 'Channel': [2], 'OrderID': [10]})
    trades = pd.DataFrame({'SecuCode': [1], 'Channel': [1], 'Price': [100], 'Volume': [10],
                           'BuyID': [10], 'SellID': [10]})
    assert reference_audit(orders, trades, 'OrderID')['buy']['matched'] == 0


def test_stream_audit_keeps_source_order_and_counts_regression_across_rows():
    rows = pd.DataFrame({'SecuCode': [1, 2, 1, 1], 'time_ms_absolute': [20, 1, 10, 10],
                         'Price': [100, 0, 100, 100], 'Volume': [1]*4,
                         'OrderID': [1, 2, 3, 3], 'OrderType': [1, -1, 1, 1]})
    result = stream_audit(rows, 'order')
    assert result['timestamp_regressions'] == 1
    assert result['duplicate_event_rows'] == 2
    assert result['nonpositive_price_rows'] == 1


def test_lagged_features_exclude_decision_day_and_retain_incomplete_history():
    days = [f'202101{i:02d}' for i in range(1, 23)]
    daily = pd.DataFrame({'SecuCode': [1]*22 + [2], 'trade_date': days + [days[-2]],
                          'amount': [2]*21 + [999999, 3], 'close': [10]*23,
                          'pre_close': [10]*23})
    basic = pd.DataFrame({'SecuCode': [1, 1], 'trade_date': [days[-2], days[-1]],
                          'circ_mv': [100, 999999]})
    result = lagged_features(daily, basic, days[-1]).set_index('SecuCode')
    assert result.loc[1, 'adv20_cny'] == 2000
    assert result.loc[1, 'market_cap_cny'] == 1000000
    assert result.loc[1, 'volatility20'] == 0
    assert np.isnan(result.loc[2, 'adv20_cny'])


def test_duplicate_daily_keys_fail_instead_of_inflating_liquidity():
    row = {'SecuCode': 1, 'trade_date': '20210101', 'amount': 2, 'close': 10, 'pre_close': 10}
    with pytest.raises(ValueError, match='duplicate'):
        lagged_features(pd.DataFrame([row, row]), pd.DataFrame(columns=['SecuCode','trade_date','circ_mv']), '20210104')


@pytest.mark.parametrize('profile', ['native_hhmmssmmm', 'relative_0930_ms'])
def test_file_sampling_selects_earliest_before_book_validation(tmp_path, monkeypatch, profile):
    import sys
    import types
    import pyarrow as pa
    import pyarrow.parquet as pq
    from market_research.studies.ashare_execution_costs.expansion import sample_books
    from market_research.studies.ashare_execution_costs.pilot import COLUMNS, measure

    native = profile == 'native_hhmmssmmm'
    security, clock = ('SecuCode','TickTime') if native else ('ticker','time_ms')
    frame = pd.DataFrame({security:[37]*3 if native else ['000037']*3,
        clock:[93000000,93001000,93100000] if native else [0,1000,60000],
        'TradingDay':[20210104]*3,'Price':[1000]*3,'TotalTurnover':[1000]*3,'TotalVolume':[100]*3})
    for side, price in [('Bid',999),('Ask',1001)]:
        for level in range(1,11):
            frame[f'{side}Price{level}'] = [price]*3
            frame[f'{side}Volume{level}'] = [100]*3
    frame.loc[0,[f'Bid{field}{level}' for field in ['Price','Volume'] for level in range(1,11)]] = 0
    path = tmp_path / 'source.parquet'
    frame.to_parquet(path,index=False)
    provider = types.ModuleType('quant_market_data_platform.l2_views')
    def batches(path, kind, columns, **kwargs):
        table = pq.read_table(path).to_pandas().rename(columns={security:'SecuCode',clock:'TickTime'})
        return iter(pa.Table.from_pandas(table[COLUMNS],preserve_index=False).to_batches())
    provider.iter_l2_batches = batches
    monkeypatch.setitem(sys.modules,'quant_market_data_platform.l2_views',provider)
    sample, stats, receipt = sample_books({'path':str(path),'days':[20210104],'clock_profile':profile},tmp_path)
    assert sample.source_row.tolist() == [0,2]
    assert stats.selected_source_rows.iloc[0] == 3
    measured, audit = measure(sample)
    assert len(measured) == 1
    assert audit['one_sided'] == 1
    assert receipt['metadata_rows'] == 3
