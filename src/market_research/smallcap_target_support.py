"""Archived three-arm target diagnostics, without prices, execution or returns."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

FACTORS = ('size_score', 'lowvol_score', 'activity_20d_score')
ARMS = ('benchmark', 'exclude_high_turnover', 'low_turnover')


def build_target_support(panel: pd.DataFrame):
    """Return security targets, support and aggregate formation diagnostics.

    Scores are archived, not PIT certified. Increasing low-turnover score means
    lower stock turnover. Each arm uses the same finite-score support; missing
    descriptors do not change membership. The first target transition is unknown.
    A source date with insufficient support resets transition history.
    """
    required = ['trade_date', 'symbol', 'industry_l1', 'signal_low_turnover', *FACTORS]
    if set(required) - set(panel):
        raise ValueError('missing target-support columns')
    frame = panel[required].copy()
    frame['trade_date'] = pd.to_datetime(frame.trade_date, errors='raise')
    if frame.empty or frame[['trade_date', 'symbol']].isna().any().any():
        raise ValueError('empty panel or missing keys')
    if frame.duplicated(['trade_date', 'symbol']).any():
        raise ValueError('duplicate formation/security keys')
    for col in ['signal_low_turnover', *FACTORS]:
        frame[col] = pd.to_numeric(frame[col], errors='raise')
    if not np.isfinite(frame.size_score).all():
        raise ValueError('finite size scores required to define cohorts')
    if np.isinf(frame[['signal_low_turnover', *FACTORS]]).any().any():
        raise ValueError('infinite descriptor or signal')
    targets, support, metrics = [], [], []
    previous = {}
    for date, day in frame.groupby('trade_date', sort=True):
        day = day.sort_values('symbol').copy()
        small = day.size_score.rank(method='first', pct=True).le(.2)
        # Keep the full archive as the common scale for both scopes.
        for factor in FACTORS:
            sd = day[factor].std(ddof=0)
            day[factor] = (day[factor] - day[factor].mean()) / sd if sd > 0 else np.nan
        for scope, cohort in [('all', day), ('smallest_20pct', day.loc[small])]:
            common = cohort.loc[cohort.signal_low_turnover.notna()].copy()
            n = len(common)
            key_date = date.date().isoformat()
            record = {'date': key_date, 'scope': scope, 'original_cohort_count': len(cohort),
                      'common_signal_count': n, 'missing_signal_count': len(cohort) - n,
                      'signal_coverage': n / len(cohort) if len(cohort) else np.nan,
                      'status': 'supported' if n >= 5 else 'insufficient_support'}
            support.append(record)
            if n < 5:
                for arm in ARMS:
                    previous.pop((scope, arm), None)
                continue
            ordered = common.sort_values(['signal_low_turnover', 'symbol'],
                                         ascending=[True, True], kind='stable')
            cut = math.ceil(n * .2)
            selections = {'benchmark': common, 'exclude_high_turnover': ordered.iloc[cut:],
                          'low_turnover': common.sort_values(
                              ['signal_low_turnover', 'symbol'], ascending=[False, True],
                              kind='stable').head(cut)}
            for arm, selected in selections.items():
                weights = pd.Series(1 / len(selected), index=selected.symbol)
                before = previous.get((scope, arm))
                change = (weights.subtract(before, fill_value=0).abs().sum() / 2
                          if before is not None else np.nan)
                previous[(scope, arm)] = weights
                for symbol, weight in weights.items():
                    targets.append({'date': key_date, 'scope': scope, 'arm': arm,
                                    'symbol': symbol, 'weight': weight})
                row = {'date': key_date, 'scope': scope, 'arm': arm, 'selected_count': len(selected),
                       'effective_holdings': 1 / float((weights ** 2).sum()),
                       'weight_sum': float(weights.sum()), 'target_change_half_l1': float(change),
                       'industry_missing_weight': float(selected.industry_l1.isna().mean())}
                for factor in FACTORS:
                    complete = selected[factor].notna().all()
                    exposure = float(selected[factor].mean()) if complete else np.nan
                    benchmark = float(common[factor].mean()) if common[factor].notna().all() else np.nan
                    row[factor + '_exposure'] = exposure
                    row[factor + '_vs_benchmark'] = exposure - benchmark
                    row[factor + '_coverage'] = float(selected[factor].notna().mean())
                metrics.append(row)
    if not targets:
        raise ValueError('no supported formation dates')
    return pd.DataFrame(targets), pd.DataFrame(support), pd.DataFrame(metrics)
