import copy

import pytest

from market_research.studies.ashare_execution_costs.minute_publication import public_projection


def proposal():
    names = ['gross_1m', 'fees_1m', 'fees_10m', 'fees_100m', 'fast_10m', 'split_10m',
             'weekly_10m', 'buffer_10m', 'minimum_1m']
    return {'schema_version': 'execution-minute-results.v1', 'complete': True,
            'expected_scenarios': 9, 'evidence': 'modeled_bar_execution_not_live_capacity',
            'inputs': {'start': '20250102', 'end': '20251231', 'sessions': 243, 'count': 40,
                       'bar_audit': {'rows': 6000000}, 'suspension_valuation_audit': {'carried_symbol_days': 30, 'max_calendar_staleness_days': 7},
                       'corporate_action_audit': {'events': 10}},
            'scenarios': [dict(scenario=name, capital_cny=1000000, execution_minutes=330,
                               release_slices=1, commission_minimum_cny=0., terminal_nav=1.1,
                               transaction_cost_cny=100., mean_one_way_turnover=.1,
                               target_notional_completion=.99, arrival_shortfall_p90_bp=20.,
                               cost_unavailable_orders=0, negative_cash_sessions=0, orders=100,
                               zero_fill_orders=1, partial_fill_orders=2, private_symbol='PRIVATE',
                               private_path='/private/input') for name in names]}


def test_public_projection_only_exports_completed_reviewable_aggregate_fields():
    result = public_projection([proposal()], {'unexplained_original': 183, 'unresolved_reobserved': 21})
    assert result['published'] is True
    assert result['windows'][0]['start'] == '2025-01-02'
    assert len(result['windows'][0]['scenarios']) == 9
    assert 'PRIVATE' not in str(result)
    assert '/private' not in str(result)
    assert result['blocked_full_2024']['unresolved_reobserved'] == 21


@pytest.mark.parametrize('change', ['partial', 'duplicate', 'negative_cash'])
def test_public_projection_rejects_incomplete_or_unfunded_scenarios(change):
    value = copy.deepcopy(proposal())
    if change == 'partial':
        value['complete'] = False
    elif change == 'duplicate':
        value['scenarios'][-1]['scenario'] = 'gross_1m'
    else:
        value['scenarios'][0]['negative_cash_sessions'] = 1
    with pytest.raises(ValueError):
        public_projection([value], {'unexplained_original': 183, 'unresolved_reobserved': 21})


def test_carried_valuations_require_staleness_evidence():
    value = proposal()
    del value['inputs']['suspension_valuation_audit']['max_calendar_staleness_days']
    with pytest.raises(ValueError, match='staleness'):
        public_projection([value], {'unexplained_original': 183, 'unresolved_reobserved': 21})
