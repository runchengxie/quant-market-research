"""Endpoint sensitivity and benchmark-relative waiting for this monthly study."""
from __future__ import annotations

import numpy as np
import pandas as pd

from market_research.recovery import analyze_recovery
from .analysis import validate_levels


def endpoint_sensitivity(frame: pd.DataFrame, asset: str, minimum_months: int = 60) -> dict:
    if type(minimum_months) is not int or minimum_months < 1:
        raise ValueError('minimum_months must be a positive integer')
    data = validate_levels(frame, [asset])
    anchors = sorted({0, *np.flatnonzero(data.date.dt.month.eq(12)).tolist(), len(data)-1})
    cells = []
    for start in anchors:
        for end in anchors:
            months = end-start
            if months < minimum_months:
                continue
            cells.append({'start': data.date.iloc[start].date().isoformat(),
                          'end': data.date.iloc[end].date().isoformat(), 'months': months,
                          'cagr': float((data[asset].iloc[end]/data[asset].iloc[start])**(12/months)-1)})
    fixed = [r for r in cells if r['start'] == data.date.iloc[0].date().isoformat()]
    return {'minimum_months': minimum_months, 'cells': cells, 'fixed_start_endpoints': fixed,
            'minimum_cagr': min((c['cagr'] for c in cells), default=None),
            'maximum_cagr': max((c['cagr'] for c in cells), default=None),
            'interpretation': 'Descriptive annual endpoint grid; cells overlap and are not independent.'}


def annual_contributions(frame: pd.DataFrame, asset: str) -> dict:
    data = validate_levels(frame, [asset])
    logs = np.log(data[asset]/data[asset].shift(1)).iloc[1:]
    intervals = pd.DataFrame({'year': data.date.iloc[1:].dt.year, 'log_growth': logs})
    total = float(logs.sum())
    rows = []
    for year, group in intervals.groupby('year'):
        value = float(group.log_growth.sum())
        rows.append({'year': int(year), 'months': len(group), 'complete_year': len(group)==12,
                     'return': float(np.expm1(value)), 'log_growth': value,
                     'share_of_total_log_growth': value/total if abs(total)>1e-12 else None})
    return {'years': rows, 'total_log_growth': total,
            'interpretation': 'Additive log-wealth contributions; negative shares and shares above 100% are possible.'}


def relative_waiting(frame: pd.DataFrame, asset: str, benchmark: str) -> dict:
    data = validate_levels(frame, [asset, benchmark])
    ratio = data[asset]/data[benchmark]
    evidence = analyze_recovery(pd.DataFrame({'date':data.date, 'nav':ratio}))
    def months(start, end):
        return int(pd.Timestamp(end).to_period('M').ordinal-pd.Timestamp(start).to_period('M').ordinal)
    episodes = evidence['episodes'].astype(object).where(pd.notna(evidence['episodes']), None).to_dict('records')
    for row in episodes:
        row['months'] = months(row['peak_date'], row['observed_until'])
    entries = evidence['entries'].astype(object).where(pd.notna(evidence['entries']), None).to_dict('records')
    for row in entries:
        row['months'] = months(row['entry_date'], row['observed_until'])
    followed = [r for r in entries if r['months'] > 0]
    completed = [r for r in episodes if not r['censored']]
    return {'asset': asset, 'benchmark': benchmark,
            'start': data.date.iloc[0].date().isoformat(), 'end':data.date.iloc[-1].date().isoformat(),
            'relative_cagr': float((ratio.iloc[-1]/ratio.iloc[0])**(12/(len(data)-1))-1),
            'relative_max_drawdown':float((ratio/ratio.cummax()-1).min()),
            'longest_observed_underperformance_months': max((r['months'] for r in episodes),default=0),
            'longest_completed_underperformance_months': max((r['months'] for r in completed),default=None),
            'current_underperformance_months': episodes[-1]['months'] if episodes and episodes[-1]['censored'] else 0,
            'no_followup_entries':len(entries)-len(followed), 'followed_entries':len(followed),
            'unrecovered_followed_entries':sum(bool(r['censored']) for r in followed),
            'episodes':episodes, 'entries':entries,
            'interpretation':'Monthly relative wealth, with unfinished intervals censored; not future waiting-time bounds.'}
