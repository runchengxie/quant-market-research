"""Audit archived signal breadth and style exposures; no returns or risk forecast.

Inputs are retained research panels, not a certified point-in-time universe.
Run from the repository root; outputs must be outside the source checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

FACTORS = ['size_score', 'lowvol_score', 'activity_20d_score',
           'illiquidity_20d_score', 'momentum_126_21d_score', 'reversal_21d_score']
SIGNALS = ['signal_low_turnover', 'signal_low_turnover_residual_size_lowvol_liquidity_returns']
COUNTS = [10, 30, 50, 100, 150, 300, 400]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def explore(panel: pd.DataFrame, counts=COUNTS):
    required = {'trade_date', 'symbol', 'industry_l1', *FACTORS, *SIGNALS}
    if required - set(panel):
        raise ValueError('missing panel columns')
    data = panel.copy()
    data['trade_date'] = pd.to_datetime(data.trade_date, errors='raise')
    if data.empty or data[['trade_date', 'symbol']].isna().any().any():
        raise ValueError('empty panel or missing identity')
    if data.duplicated(['trade_date', 'symbol']).any():
        raise ValueError('duplicate formation/security keys')
    if not counts or any(not isinstance(k, int) or k <= 0 for k in counts):
        raise ValueError('counts must be positive integers')
    for c in [*FACTORS, *SIGNALS]:
        data[c] = pd.to_numeric(data[c], errors='raise')
        if np.isinf(data[c]).any():
            raise ValueError('infinite score')
    if data.size_score.isna().any():
        raise ValueError('size missing; cannot define smallest cohort')
    rows, correlations = [], []
    coverage = data[FACTORS + SIGNALS].notna().mean().to_dict()
    for date, daily in data.groupby('trade_date', sort=True):
        daily = daily.sort_values('symbol').copy()
        # Use all available observations per descriptor, never a future-return filter.
        for f in FACTORS:
            sd = daily[f].std(ddof=0)
            daily[f] = (daily[f] - daily[f].mean()) / sd if sd > 0 else np.nan
        small = daily.size_score.rank(method='first', pct=True).le(.2)
        for scope, universe in [('all', daily), ('smallest_20pct', daily.loc[small])]:
            for signal in SIGNALS:
                ordered = universe.dropna(subset=[signal]).sort_values(
                    [signal, 'symbol'], ascending=[False, True], kind='stable')
                for f in FACTORS:
                    pair = universe[[signal, f]].dropna()
                    correlations.append({'date': date.isoformat(), 'scope': scope,
                                         'signal': signal, 'factor': f, 'pairs': len(pair),
                                         'spearman': pair[signal].rank().corr(pair[f].rank())})
                for k in counts:
                    selected = ordered.head(k)
                    n = len(selected)
                    if not n:
                        continue
                    for gamma in [0., .5]:
                        q = np.arange(n, 0, -1) / n
                        w = q ** gamma
                        w /= w.sum()
                        row = {'date': date.isoformat(), 'scope': scope, 'signal': signal,
                               'k': k, 'gamma': gamma, 'selected_count': n,
                               'eligible_signal_count': len(ordered), 'shortfall': n < k,
                               'effective_holdings': 1 / sum(w*w), 'max_weight': max(w),
                               'industry_missing_weight': float(w[selected.industry_l1.isna()].sum())}
                        industries = pd.Series(w).groupby(
                            selected.industry_l1.fillna('UNKNOWN').reset_index(drop=True)).sum()
                        row['industry_hhi'] = float(sum(industries ** 2))
                        for f in FACTORS:
                            valid = selected[f].notna().to_numpy()
                            mass = w[valid].sum()
                            # No exposure estimate unless every selected holding has the descriptor.
                            exposure = float(w @ selected[f]) if valid.all() else np.nan
                            row[f + '_coverage'] = float(mass)
                            row[f + '_vs_all'] = exposure  # Full-universe descriptor mean is zero.
                            row[f + '_vs_local'] = exposure - universe[f].mean()
                        rows.append(row)
    detail = pd.DataFrame(rows)
    # Match formation dates across signals and scopes before comparing means.
    combinations = len(SIGNALS) * 2
    support = detail[['date', 'scope', 'signal']].drop_duplicates().groupby('date').size()
    common_dates = support.index[support.eq(combinations)]
    detail = detail.loc[detail.date.isin(common_dates)].copy()
    keys = ['scope', 'signal', 'k', 'gamma']
    metrics = [c for c in detail if c not in keys + ['date']]
    summary = detail.groupby(keys)[metrics].mean().reset_index()
    dates = detail.groupby(keys).date.nunique().rename('formation_dates').reset_index()
    summary = summary.merge(dates, on=keys, validate='one_to_one')
    valid_counts = detail.groupby(keys)[metrics].count().add_suffix('_valid_dates').reset_index()
    summary = summary.merge(valid_counts, on=keys, validate='one_to_one')
    correlations = pd.DataFrame(correlations)
    correlations = correlations.loc[correlations.date.isin(common_dates)]
    correlation_summary = correlations.groupby(['scope', 'signal', 'factor']).agg(
        mean_spearman=('spearman', 'mean'), valid_dates=('spearman', 'count'),
        min_pairs=('pairs', 'min')).reset_index()
    return detail, summary, correlation_summary, coverage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--panel', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    repo = Path(__file__).resolve().parents[1]
    if output == repo or repo in output.parents:
        raise ValueError('output must be outside source checkout')
    output.mkdir(parents=True, exist_ok=False)
    detail, summary, corr, coverage = explore(pd.read_parquet(args.panel))
    detail.to_csv(output / 'formation_exposures.csv', index=False)
    summary.to_csv(output / 'breadth_summary.csv', index=False)
    corr.to_csv(output / 'signal_correlations.csv', index=False)
    manifest = {'schema': 'smallcap-style-breadth.v1', 'stage': 'retrospective_exposure_diagnostic',
                'input_sha256': sha(args.panel), 'script_sha256': sha(Path(__file__)),
                'coverage': coverage, 'formation_start': detail.date.min(),
                'formation_end': detail.date.max(), 'formation_dates': detail.date.nunique(),
                'input_formation_dates': pd.read_parquet(args.panel, columns=['trade_date']).trade_date.nunique(),
                'comparison': 'common formation dates across both signals and both scopes',
                'rows': len(detail), 'returns_estimated': False, 'risk_forecast': False,
                'pit_certified': False, 'cash_policy': 'resize available names, flag shortfall',
                'missing_exposure_policy': 'unknown unless all selected holdings observed',
                'standardization': 'per date full archived universe mean/population sd; no new clipping',
                'outputs': {p.name: sha(p) for p in sorted(output.glob('*.csv'))}}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
