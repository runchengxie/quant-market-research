"""Finite, predeclared monthly allocation scenarios for this study only.

This is an idealized wealth-accounting diagnostic, not a general backtester,
order simulator, execution model or live allocation recommendation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .analysis import holding_periods, validate_levels

POLICIES = ('buy_hold', 'annual', 'threshold_5pp')


def compare_allocation(frame: pd.DataFrame, weights: dict[str,float], policy: str,
                       cost_bps: float = 0) -> dict:
    targets = np.array(list(weights.values()),dtype=float)
    if (not weights or not np.isfinite(targets).all() or (targets<0).any()
            or abs(targets.sum()-1)>1e-10 or policy not in POLICIES
            or not np.isfinite(cost_bps) or not 0<=cost_bps<10000):
        raise ValueError('invalid study policy, weights or transaction cost')
    cols = list(weights)
    data = validate_levels(frame, cols+(['cpi'] if 'cpi' in frame else []))
    returns = data[cols].pct_change(fill_method=None).fillna(0).to_numpy()
    gross_holdings, holdings = targets.copy(), targets.copy()
    rate = cost_bps/10000
    paths=[]
    total_cost=turnover=0.
    for i,(date,ret) in enumerate(zip(data.date,returns)):
        holdings *= 1+ret
        gross_holdings *= 1+ret
        before = float(holdings.sum())
        actual_weights=holdings/before
        rebalance=(0<i<len(data)-1 and (
            (policy=='annual' and i%12==0)
            or (policy=='threshold_5pp' and np.max(np.abs(actual_weights-targets))>=.05-1e-12)))
        fee=traded=0.
        if rebalance:
            # Cost paid out of this account changes target trade amounts.
            # Solve fee = rate * sum(abs(target*(wealth-fee)-holdings)).
            if rate:
                low, high=0.,before
                for _ in range(64):
                    candidate=(low+high)/2
                    required=rate*float(np.abs(targets*(before-candidate)-holdings).sum())
                    if candidate>required:
                        high=candidate
                    else:
                        low=candidate
                fee=(low+high)/2
            traded=float(np.abs(targets*(before-fee)-holdings).sum())
            holdings=targets*(before-fee)
            gross_holdings=targets*float(gross_holdings.sum())
            turnover+=traded/before
            total_cost+=fee
        paths.append({'date':date.date().isoformat(),'wealth':float(holdings.sum()),
                      'gross_wealth':float(gross_holdings.sum()),'rebalance':bool(rebalance),
                      'cost_paid':fee,'traded_notional':traded,
                      'post_weights':dict(zip(cols,(holdings/holdings.sum()).tolist())),
                      'post_holdings':dict(zip(cols,holdings.tolist()))})
    wealth=pd.Series([p['wealth'] for p in paths])
    gross=pd.Series([p['gross_wealth'] for p in paths])
    risk_frame=pd.DataFrame({'date':data.date,'total':wealth})
    if 'cpi' in data:
        risk_frame['cpi']=data.cpi
    risk=holding_periods(risk_frame)
    ten=next(r for r in risk['horizons'] if r['months']==120)
    peak=wealth.cummax()
    active_start=None
    longest=0
    for i in range(len(wealth)):
        if wealth.iloc[i]>=peak.iloc[i]-1e-12:
            if active_start is not None:
                longest=max(longest,i-active_start)
            active_start=None
        else:
            if active_start is None:
                active_start=i-1
            longest=max(longest,i-active_start)
    n=len(data)-1
    return {'policy':policy,'target_weights':weights,'cost_bps_per_traded_notional':cost_bps,
            'start':paths[0]['date'],'end':paths[-1]['date'],'months':n,
            'summary':{'net_cagr':float(wealth.iloc[-1]**(12/n)-1),
                       'gross_cagr':float(gross.iloc[-1]**(12/n)-1),
                       'net_max_drawdown':float((wealth/wealth.cummax()-1).min()),
                       'rebalance_count':sum(p['rebalance'] for p in paths),
                       'annualized_two_sided_turnover':turnover*12/n,
                       'cost_paid_per_initial_capital':total_cost,
                       'longest_observed_underwater_months':longest,
                       'ten_year_nominal_loss_fraction':ten['nominal_loss_fraction'],
                       'ten_year_real_loss_fraction':ten['real_loss_fraction'],
                       'ten_year_completed_windows':ten['completed_windows']},
            'path':paths,
            'assumptions':['Month-end marks and simultaneous fractional trading.',
                           'Current-month return precedes rebalance, affecting subsequent returns.',
                           'Initial purchase and final liquidation excluded; no leverage or interest.',
                           'Cost is a sensitivity on both buys and sells, not calibrated execution.']}
