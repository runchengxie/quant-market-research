import pandas as pd
import pytest
from market_research.studies.ashare_execution_costs.replay import snapshot_path, replay_gate


def book(t, p=101, q=10):
    return {'time_ms':t, 'AskPrice1':p, 'AskVolume1':q, 'BidPrice1':99, 'BidVolume1':10}


def test_cash_budget_and_duplicate_instant_depth_are_conserved():
    result = snapshot_path(pd.DataFrame([book(0), book(0), book(10)]),
                           quantity=30, budget_cny=15, mode='twap', side='buy', horizon_ms=20, interval_ms=10)
    assert result['filled_quantity'] == 14
    assert result['cash_cny'] == pytest.approx(14.14)
    assert result['remaining_quantity'] == 16
    assert result['instants'] == 2


def test_market_only_uses_first_quote_and_twap_uses_future_execution_clock():
    path = pd.DataFrame([book(0), book(10, 110)])
    market = snapshot_path(path, quantity=20, budget_cny=100, mode='market', side='buy')
    twap = snapshot_path(path, quantity=20, budget_cny=100, mode='twap', side='buy', horizon_ms=20, interval_ms=10)
    assert market['filled_quantity'] == 10
    assert twap['filled_quantity'] == 20
    assert twap['cash_cny'] == pytest.approx(21.1)


def test_limit_wait_does_not_fill_when_limit_never_crosses():
    result = snapshot_path(pd.DataFrame([book(0), book(10)]), quantity=20,
                           budget_cny=100, mode='limit_wait', side='buy')
    assert result['filled_quantity'] == 0
    assert result['optimistic_passive_quantity_upper_bound'] == 20


def test_missing_semantic_and_order_evidence_blocks_replay():
    gate = replay_gate(semantics_verified=False, exchange_order_verified=False)
    assert gate['full_book_replay'] == 'blocked'
    assert gate['snapshot_reconciliation'] == 'not_run'


def test_future_quotes_cannot_change_first_market_fill():
    a = snapshot_path(pd.DataFrame([book(0), book(10, 1000)]), quantity=20,
                      budget_cny=100, mode='market', side='buy')
    b = snapshot_path(pd.DataFrame([book(0), book(10, 1)]), quantity=20,
                      budget_cny=100, mode='market', side='buy')
    assert a['cash_cny'] == b['cash_cny']


def test_multilevel_cash_uses_each_level_price_and_sell_quantity_conserves():
    row = book(0)
    row.update(AskPrice2=110, AskVolume2=10)
    buy = snapshot_path(pd.DataFrame([row]), quantity=15, budget_cny=100,
                        mode='market', side='buy')
    sell = snapshot_path(pd.DataFrame([row]), quantity=15, budget_cny=0,
                         mode='market', side='sell')
    assert buy['cash_cny'] == pytest.approx(15.6)
    assert sell['filled_quantity'] + sell['remaining_quantity'] == 15
    assert sell['cash_cny'] == 9.9


def test_invalid_cash_does_not_create_fills():
    with pytest.raises(ValueError):
        snapshot_path(pd.DataFrame([book(0)]), quantity=10, budget_cny=float('nan'),
                      mode='market', side='buy')


def test_twap_release_does_not_use_future_snapshot_count():
    a = snapshot_path(pd.DataFrame([book(0), book(10)]), quantity=20,
                      budget_cny=100, mode='twap', side='buy', horizon_ms=20, interval_ms=10)
    b = snapshot_path(pd.DataFrame([book(0), book(5), book(10)]), quantity=20,
                      budget_cny=100, mode='twap', side='buy', horizon_ms=20, interval_ms=10)
    assert a['fills'][0]['quantity'] == b['fills'][0]['quantity'] == 10


@pytest.mark.parametrize('side,execution,opportunity,total', [
    ('buy', .1, 1, 550), ('sell', .1, -1, -450)])
def test_partial_shortfall_signed_accounting(side, execution, opportunity, total):
    terminal = book(100, 111)
    terminal['BidPrice1'] = 109
    r = snapshot_path(pd.DataFrame([book(0), terminal]), quantity=20,
                      budget_cny=100, mode='market', side=side, horizon_ms=100)
    assert r['execution_cost_cny'] == pytest.approx(execution)
    assert r['opportunity_cost_cny'] == pytest.approx(opportunity)
    assert r['total_shortfall_bp'] == pytest.approx(total)
    assert r['completion_duration_ms'] is None


def test_zero_fill_has_opportunity_cost_and_no_completion_time():
    terminal = book(100, 111)
    terminal['BidPrice1'] = 109
    r = snapshot_path(pd.DataFrame([book(0), terminal]), quantity=20,
                      budget_cny=0, mode='market', side='buy', horizon_ms=100)
    assert r['execution_cost_cny'] == 0
    assert r['opportunity_cost_cny'] == pytest.approx(2)
    assert r['total_shortfall_bp'] == pytest.approx(1000)
    assert r['completion_duration_ms'] is None


@pytest.mark.parametrize('terminal', [book(100), book(100, 90),
    {'time_ms':100, 'AskPrice1':0, 'AskVolume1':0, 'BidPrice1':99, 'BidVolume1':10}])
def test_stale_or_invalid_terminal_keeps_opportunity_cost_missing(terminal):
    horizon = 100000 if terminal['AskPrice1'] == 101 else 100
    r = snapshot_path(pd.DataFrame([book(0), terminal]), quantity=20,
                      budget_cny=100, mode='market', side='buy', horizon_ms=horizon)
    assert r['execution_cost_cny'] == pytest.approx(.1)
    assert r['opportunity_cost_cny'] is None
    assert r['total_shortfall_bp'] is None


def test_future_evaluation_quote_changes_only_market_opportunity_cost():
    low, high = book(100, 103), book(100, 111)
    low['BidPrice1'], high['BidPrice1'] = 101, 109
    values = [snapshot_path(pd.DataFrame([book(0), t]), quantity=20,
                           budget_cny=100, mode='market', side='buy', horizon_ms=100)
              for t in (low, high)]
    assert values[0]['fills'] == values[1]['fills']
    assert values[0]['execution_cost_cny'] == values[1]['execution_cost_cny']
    assert values[0]['opportunity_cost_cny'] != values[1]['opportunity_cost_cny']


def test_full_fill_completion_duration_and_zero_unfilled_cost():
    r = snapshot_path(pd.DataFrame([book(0), book(10)]), quantity=20,
                      budget_cny=100, mode='twap', side='buy', horizon_ms=20, interval_ms=10)
    assert r['completion_duration_ms'] == 10
    assert r['opportunity_cost_cny'] == 0


def test_sell_zero_fill_limit_wait_has_signed_opportunity_cost():
    terminal = book(100, 91)
    terminal['BidPrice1'] = 89
    r = snapshot_path(pd.DataFrame([book(0), terminal]), quantity=20,
                      budget_cny=100, mode='limit_wait', side='sell', horizon_ms=100)
    assert r['filled_quantity'] == 0
    assert r['execution_cost_cny'] == 0
    assert r['opportunity_cost_cny'] == pytest.approx(2)
    assert r['total_shortfall_bp'] == pytest.approx(1000)
    assert r['completion_duration_ms'] is None
