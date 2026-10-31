"""Financial counterexamples for the asset-return study."""
import numpy as np
import pandas as pd
import pytest

from market_research.studies.asset_returns.analysis import (
    validate_levels, return_sources, holding_periods, relative_premium,
    diversification, cash_paths, earnings_attribution,
)


def levels(values, **extra):
    return pd.DataFrame({'date': pd.date_range('2020-01-31', periods=len(values), freq='ME'),
                         'price': values, **extra})


def test_geometric_dividend_component_reconciles():
    result = return_sources(levels([100, 110, 121], total=[100, 112, 125.44]))
    assert (1 + result['price_cagr']) * (1 + result['distribution_component_cagr']) == pytest.approx(1 + result['total_cagr'])
    assert result['distribution_component_is_cash_yield'] is False


@pytest.mark.parametrize('frame', [levels([100, np.nan]), levels([100, np.inf]),
    levels([100, 0]), levels([100, 101]).iloc[[0, 0]],
    levels([100, 101, 102]).iloc[[0, 2]]])
def test_rejects_invalid_or_missing_months(frame):
    with pytest.raises(ValueError):
        validate_levels(frame, ['price'])


def test_horizons_preserve_censoring_and_nominal_vs_real():
    frame = levels([100, 90, 95, 105], total=[100, 90, 95, 105], cpi=[100, 102, 104, 106])
    result = holding_periods(frame, horizons=(2,))
    row = result['horizons'][0]
    assert row['completed_windows'] == 2
    assert row['incomplete_windows'] == 2
    assert row['nominal_loss_fraction'] == .5
    assert row['real_loss_fraction'] == .5
    assert row['worst_path_drawdown'] == pytest.approx(-.1)
    assert row['worst_real_annualized_return'] < row['worst_annualized_return']
    assert result['recovery']['unrecovered_entry_count'] == 1  # final entry still censored
    assert result['real_recovery']['unrecovered_entry_count'] == 2
    assert all(r['breakeven_date'] is None for r in result['real_recovery_entries'] if r['censored'])


def test_relative_premium_uses_wealth_ratio_and_initial_capital():
    frame = levels([100, 90, 81], total=[100, 90, 81], benchmark=[100, 100, 100])
    r = relative_premium(frame, 'total', 'benchmark')
    assert r['relative_terminal_wealth'] == pytest.approx(.81)
    assert r['relative_max_drawdown'] == pytest.approx(-.19)
    assert r['negative_relative_month_fraction'] == 1


def test_diversification_uses_shared_complete_months_and_down_markets():
    frame = levels([100, 90, 99, 89.1], stock=[100, 90, 99, 89.1], bond=[100, 102, 101, 103])
    r = diversification(frame, ['stock', 'bond'], 'stock', rolling_months=2)
    assert r['observations'] == 3
    assert r['down_market']['bond']['months'] == 2
    assert r['down_market']['bond']['positive_fraction'] == 1
    assert len(r['rolling_correlations']) == 2


def test_cash_taken_out_is_part_of_wealth_but_not_reinvested():
    frame = levels([100, 90, 90], cash_per_unit=[0, 10, 0])
    r = cash_paths(frame, initial_capital=100)
    assert r.iloc[1]['asset_value'] == 90
    assert r.iloc[1]['cash_balance'] == 10
    assert r.iloc[1]['total_wealth'] == 100
    assert r.iloc[2]['units'] == 1


def test_withdrawals_use_cash_first_and_report_shortfall():
    frame = levels([100, 90, 45], cash_per_unit=[0, 10, 0])
    r = cash_paths(frame, initial_capital=100, fixed_withdrawal=60, sale_cost_bps=100)
    assert r.iloc[1]['withdrawn'] == pytest.approx(60)
    assert r.iloc[1]['sale_cost'] == pytest.approx(50 / 99)
    assert r.iloc[2]['shortfall'] > 0
    assert r.iloc[2]['units'] == 0


def test_earnings_identity_is_distinguished_from_independent_evidence():
    f = levels([100, 120], pe=[10, 12])
    r = earnings_attribution(f)
    assert r['earnings_source'] == 'inferred_price_divided_by_pe'
    assert r['independent_fundamentals_validation'] is False
    assert r['eps_growth'] == pytest.approx(0)
    with pytest.raises(ValueError):
        earnings_attribution(levels([100, 120], pe=[10, -12]))


def test_cash_paths_reject_invalid_parameters():
    f = levels([100, 100], cash_per_unit=[0, 0])
    for kwargs in ({'withdrawal_rate': 1.1}, {'fixed_withdrawal': -1},
                   {'sale_cost_bps': 10000}, {'initial_capital': 0}):
        with pytest.raises(ValueError):
            cash_paths(f, **kwargs)


def test_fx_conversion_retains_interaction_and_cpi_uses_mom():
    from market_research.studies.asset_returns.analysis import convert_currency, chain_cpi
    f = levels([100, 110], target_per_local=[7, 7.7])
    assert convert_currency(f, 'price').iloc[-1] / convert_currency(f, 'price').iloc[0] == pytest.approx(1.21)
    cpi = pd.DataFrame({'date': f.date, 'mom_pct': [99, 1]})
    assert chain_cpi(cpi).tolist() == [100, 101]
    with pytest.raises(ValueError):
        chain_cpi(cpi.assign(mom_pct=[0, np.nan]))


def test_monthly_mix_cost_is_separate_sensitivity():
    from market_research.studies.asset_returns.analysis import monthly_mix
    f = levels([100, 90, 99], equity=[100, 90, 99], gold=[100, 110, 110])
    r = monthly_mix(f, {'equity': .5, 'gold': .5}, annual_cost_drag=.01)
    assert r['gross_terminal_wealth'] == pytest.approx(1.05)
    assert r['net_terminal_wealth'] == pytest.approx(1.05 * .99 ** (2 / 12))
    assert r['gross_max_drawdown'] == pytest.approx(0)
    with pytest.raises(ValueError):
        monthly_mix(f, {'equity': 1.1, 'gold': -.1})
