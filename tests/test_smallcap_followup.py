import pytest
from market_research.smallcap_followup import select_buffered, replacement_fraction, quote_diagnostics


def test_buffer_reduces_boundary_churn_but_removes_ineligible():
    previous = ['a', 'b']
    ranked = ['c', 'a', 'b', 'd']
    plain = select_buffered(ranked, previous, 2, 2)
    buffered = select_buffered(ranked, previous, 2, 3)
    assert replacement_fraction(previous, plain) == .5
    assert replacement_fraction(previous, buffered) == 0
    assert select_buffered(['c', 'a', 'd'], previous, 2, 3) == ['a', 'c']
    assert replacement_fraction([], buffered) is None
    with pytest.raises(ValueError):
        select_buffered(['a'], [], 2, 3)


def test_diagnostics_reject_missing_windows_and_preserve_missing_fresh_spreads():
    row = dict(ticker='X', trade_date='2025-01-02', label='open', covered_seconds=1800,
               valid_seconds=1800, bid_size_seconds=1800, fresh60_seconds=0,
               tw_spread_bps=10, fresh60_tw_spread_bps=None, tw_best_bid_dollars=2000,
               bid_covers_1000_fraction=1, bid_covers_10000_fraction=0)
    with pytest.raises(ValueError, match='Missing intraday'):
        quote_diagnostics([row], {'2025-01-02'}, set())
    rows = [dict(row, label=label, trade_date=day) for day in ['2025-01-02', '2025-01-03']
            for label in ['open', 'midday', 'close']]
    out = quote_diagnostics(rows, {'2025-01-02'}, {'2025-01-03'})
    assert out['paired'][0]['fresh60_tw_spread_bps']['baseline'] is None
    with pytest.raises(ValueError, match='Duplicate'):
        quote_diagnostics(rows + [row], {'2025-01-02'}, {'2025-01-03'})
