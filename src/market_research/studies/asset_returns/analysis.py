"""Descriptive diagnostics for the long-horizon asset-return study.

All levels are month-end observations, denominated in a common currency.
No inference of executable returns or forward expected premia is made.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from market_research.recovery import analyze_recovery


def validate_levels(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    data = frame[['date', *columns]].copy()
    data['date'] = pd.to_datetime(data['date'], errors='raise')
    if len(data) < 2 or data.date.isna().any():
        raise ValueError('at least two nonmissing monthly dates are required')
    data = data.sort_values('date').reset_index(drop=True)
    months = data.date.dt.to_period('M')
    if months.duplicated().any() or not data.date.dt.is_month_end.all():
        raise ValueError('one observation per calendar month end is required')
    if not np.all(np.diff(months.astype('int64')) == 1):
        raise ValueError('missing months cannot be filled or skipped')
    for col in columns:
        data[col] = pd.to_numeric(data[col], errors='raise')
        if not np.isfinite(data[col]).all() or (data[col] <= 0).any():
            raise ValueError(f'{col} must contain finite positive levels')
    return data


def _cagr(values: pd.Series) -> float:
    return float((values.iloc[-1] / values.iloc[0]) ** (12 / (len(values) - 1)) - 1)


def return_sources(frame: pd.DataFrame) -> dict:
    data = validate_levels(frame, ['price', 'total'])
    ratio = data.total / data.price
    return {
        'price_cagr': _cagr(data.price), 'total_cagr': _cagr(data.total),
        'distribution_component_cagr': _cagr(ratio),
        'distribution_component_is_cash_yield': False,
        'months': len(data) - 1,
        'interpretation': 'Geometric total/price residual; not cash received or an independent driver.',
    }


def holding_periods(frame: pd.DataFrame, horizons=(12, 36, 60, 120)) -> dict:
    columns = ['total'] + (['cpi'] if 'cpi' in frame else [])
    data = validate_levels(frame, columns)
    nominal = data.total
    real = nominal / data.cpi if 'cpi' in data else None
    rows = []
    for months in horizons:
        if type(months) is not int or months <= 0:
            raise ValueError('horizons must be positive integer months')
        returns = (nominal.shift(-months) / nominal - 1).iloc[:max(0, len(data) - months)]
        real_returns = ((real.shift(-months) / real - 1).iloc[:len(returns)]
                        if real is not None else None)
        rows.append({
            'months': months, 'completed_windows': len(returns),
            'worst_path_drawdown': min((float((nominal.iloc[i:i + months + 1] / nominal.iloc[i:i + months + 1].cummax() - 1).min()) for i in range(len(returns))), default=None),
            'worst_real_annualized_return': float((1 + real_returns.min()) ** (12 / months) - 1) if real_returns is not None and len(returns) else None,
            'incomplete_windows': min(months, len(data)),
            'nominal_loss_fraction': float((returns < 0).mean()) if len(returns) else None,
            'real_loss_fraction': (float((real_returns < 0).mean())
                                   if real_returns is not None and len(returns) else None),
            'worst_annualized_return': float((1 + returns.min()) ** (12 / months) - 1) if len(returns) else None,
            'median_annualized_return': float((1 + returns.median()) ** (12 / months) - 1) if len(returns) else None,
        })
    recovery = analyze_recovery(pd.DataFrame({'date': data.date, 'nav': nominal}))
    real_recovery = (analyze_recovery(pd.DataFrame({'date': data.date, 'nav': real}))
                     if real is not None else None)
    return {
        'horizons': rows, 'recovery': recovery['summary'],
        'recovery_entries': recovery['entries'].astype(object).where(pd.notna(recovery['entries']), None).to_dict('records'),
        'real_recovery': real_recovery['summary'] if real_recovery else None,
        'real_recovery_entries': real_recovery['entries'].astype(object).where(pd.notna(recovery['entries']), None).to_dict('records') if real_recovery else None,
        'sampling': 'monthly; overlapping windows are not independent observations',
    }


def relative_premium(frame: pd.DataFrame, asset: str, benchmark: str) -> dict:
    data = validate_levels(frame, [asset, benchmark])
    wealth = (data[asset] / data[asset].iloc[0]) / (data[benchmark] / data[benchmark].iloc[0])
    returns = wealth.pct_change(fill_method=None).iloc[1:]
    recovery = analyze_recovery(pd.DataFrame({'date': data.date, 'nav': wealth}))
    return {
        'relative_cagr': _cagr(wealth), 'relative_terminal_wealth': float(wealth.iloc[-1]),
        'relative_max_drawdown': float((wealth / wealth.cummax() - 1).min()),
        'negative_relative_month_fraction': float((returns < 0).mean()),
        'recovery': recovery['summary'], 'recovery_entries': recovery['entries'].astype(object).where(pd.notna(recovery['entries']), None).to_dict('records'),
        'interpretation': 'Realized relative wealth; not a causal or expected risk premium.',
    }


def diversification(frame: pd.DataFrame, assets: list[str], equity: str,
                    rolling_months: int = 36) -> dict:
    if equity not in assets or len(set(assets)) != len(assets) or len(assets) < 2:
        raise ValueError('provide distinct assets including the equity reference')
    if type(rolling_months) is not int or rolling_months < 2:
        raise ValueError('rolling window must be at least two months')
    data = validate_levels(frame, assets)
    returns = data[assets].pct_change(fill_method=None).iloc[1:]
    down = returns.loc[returns[equity] < 0]
    corr = returns.corr()
    rolling = []
    for end in range(rolling_months, len(returns) + 1):
        window = returns.iloc[end - rolling_months:end]
        values = window.corr()[equity]
        rolling.append({'date': data.date.iloc[end].date().isoformat(),
                        **{a: float(values[a]) if pd.notna(values[a]) else None for a in assets}})
    return {
        'observations': len(returns), 'frequency': 'monthly',
        'correlation': {a: {b: float(corr.loc[a, b]) if pd.notna(corr.loc[a, b]) else None
                            for b in assets} for a in assets},
        'rolling_correlations': rolling,
        'down_market': {a: {'months': len(down),
                            'mean_return': float(down[a].mean()) if len(down) else None,
                            'positive_fraction': float((down[a] > 0).mean()) if len(down) else None,
                            'worst_return': float(down[a].min()) if len(down) else None}
                        for a in assets},
    }


def earnings_attribution(frame: pd.DataFrame) -> dict:
    # Index-level P = EPS * PE is an identity, not causal financial evidence.
    data = validate_levels(frame, ['price', 'pe'] + (['eps'] if 'eps' in frame else []))
    inferred = 'eps' not in data
    eps = data.price / data.pe if inferred else data.eps
    price_ratio = float(data.price.iloc[-1] / data.price.iloc[0])
    eps_ratio = float(eps.iloc[-1] / eps.iloc[0])
    pe_ratio = float(data.pe.iloc[-1] / data.pe.iloc[0])
    return {
        'price_growth': price_ratio - 1, 'eps_growth': eps_ratio - 1,
        'pe_growth': pe_ratio - 1,
        'reconciliation_residual': price_ratio - eps_ratio * pe_ratio,
        'earnings_source': 'inferred_price_divided_by_pe' if inferred else 'supplied_eps_requires_scope_audit',
        'independent_fundamentals_validation': False,
        'interpretation': 'Dynamic-index accounting; constituent changes and share issuance are unresolved.',
    }


def cash_paths(frame: pd.DataFrame, initial_capital: float = 1,
               fixed_withdrawal: float = 0, withdrawal_rate: float = 0,
               sale_cost_bps: float = 0) -> pd.DataFrame:
    """Monthly cash scenario, not an ex-date/payment-date entitlement engine.

Requires split-adjusted unit prices and corresponding cash per unit. Cash is
assumed both entitled and paid at each month end on the previous month's
units, before withdrawals. No reinvestment, interest or tax is assumed.
Do not apply directly to raw distributions spanning different payment months.
    """
    params = [initial_capital, fixed_withdrawal, withdrawal_rate, sale_cost_bps]
    if (not np.isfinite(params).all() or initial_capital <= 0 or fixed_withdrawal < 0
            or not 0 <= withdrawal_rate <= 1 or not 0 <= sale_cost_bps < 10000):
        raise ValueError('invalid capital, withdrawal or transaction cost')
    data = validate_levels(frame, ['price'])
    cash = pd.to_numeric(frame.set_index(pd.to_datetime(frame.date))['cash_per_unit'], errors='raise')
    cash = cash.reindex(data.date).to_numpy(dtype=float)
    if not np.isfinite(cash).all() or (cash < 0).any() or cash[0] != 0:
        raise ValueError('cash must be finite, nonnegative; entry month cash must be zero')
    units, balance, withdrawn_total, fees_total = initial_capital / data.price.iloc[0], 0., 0., 0.
    rows = []
    for i, row in enumerate(data.itertuples(index=False)):
        received = units * cash[i]
        balance += received
        requested = (fixed_withdrawal + withdrawal_rate * (units * row.price + balance)) if i else 0.
        from_cash = min(balance, requested)
        balance -= from_cash
        short = requested - from_cash
        rate = sale_cost_bps / 10000
        sale = min(units * row.price, short / (1 - rate))
        fee = sale * rate
        units = max(0., units - sale / row.price)
        actual = from_cash + sale - fee
        withdrawn_total += actual
        fees_total += fee
        rows.append({'date': row.date.date().isoformat(), 'units': units,
                     'asset_value': units * row.price, 'cash_balance': balance,
                     'cash_received': received, 'requested': requested, 'withdrawn': actual,
                     'shortfall': max(0., requested - actual), 'sale_cost': fee,
                     'total_wealth': units * row.price + balance,
                     'wealth_plus_withdrawals': units * row.price + balance + withdrawn_total,
                     'cumulative_withdrawn': withdrawn_total, 'cumulative_sale_cost': fees_total})
    return pd.DataFrame(rows)


def convert_currency(frame: pd.DataFrame, asset: str) -> pd.Series:
    """Convert levels using target-currency units per one local-currency unit."""
    data = validate_levels(frame, [asset, 'target_per_local'])
    return data[asset] * data.target_per_local


def chain_cpi(frame: pd.DataFrame) -> pd.Series:
    data = validate_levels(frame.assign(_placeholder=1.), ['_placeholder'])
    rates = pd.to_numeric(frame.set_index(pd.to_datetime(frame.date))['mom_pct'], errors='raise')
    rates = rates.reindex(data.date).reset_index(drop=True)
    if not np.isfinite(rates).all() or (rates <= -100).any():
        raise ValueError('CPI monthly rates must be finite and greater than -100 percent')
    factors = 1 + rates / 100
    factors.iloc[0] = 1  # first observation is a base level, not a return interval
    return factors.cumprod() * 100


def monthly_mix(frame: pd.DataFrame, weights: dict[str, float],
                annual_cost_drag: float = 0) -> dict:
    """Constant-weight monthly diagnostic, frictionless simultaneous rebalancing.

The annual drag is a declared sensitivity, not calibrated execution costs.
    """
    values = np.array(list(weights.values()), dtype=float)
    if (not weights or not np.isfinite(values).all() or (values < 0).any()
            or abs(values.sum() - 1) > 1e-10
            or not np.isfinite(annual_cost_drag) or not 0 <= annual_cost_drag < 1):
        raise ValueError('nonnegative weights must sum to one; annual drag must be in [0,1)')
    data = validate_levels(frame, list(weights))
    returns = data[list(weights)].pct_change(fill_method=None).iloc[1:]
    gross = returns.mul(pd.Series(weights)).sum(axis=1)
    gross_nav = pd.Series(np.r_[1., (1 + gross).cumprod().to_numpy()])
    net_nav = pd.Series(np.r_[1., ((1 + gross) * (1 - annual_cost_drag) ** (1 / 12)).cumprod().to_numpy()])
    return {
        'weights': weights, 'months': len(gross), 'gross_cagr': _cagr(gross_nav),
        'net_cagr': _cagr(net_nav), 'gross_terminal_wealth': float(gross_nav.iloc[-1]),
        'net_terminal_wealth': float(net_nav.iloc[-1]),
        'gross_max_drawdown': float((gross_nav / gross_nav.cummax() - 1).min()),
        'net_max_drawdown': float((net_nav / net_nav.cummax() - 1).min()),
        'annual_cost_drag': annual_cost_drag,
        'cost_status': 'assumed annual wealth drag; not observed execution costs',
        'rebalance': 'idealized simultaneous month end; not an executable backtest',
    }
