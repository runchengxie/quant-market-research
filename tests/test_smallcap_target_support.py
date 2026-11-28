import numpy as np
import pandas as pd
import pytest

from market_research.smallcap_target_support import build_target_support


def panel():
    p = pd.DataFrame({'trade_date': ['2020-01-31'] * 30,
                      'symbol': [f'S{i:02}' for i in range(30)],
                      'industry_l1': ['A'] * 30,
                      'size_score': np.arange(30, dtype=float),
                      'signal_low_turnover': np.arange(30, dtype=float),
                      'lowvol_score': np.arange(30, dtype=float),
                      'activity_20d_score': np.arange(30, dtype=float)})
    return p


def test_three_arms_have_common_support_and_normalized_weights():
    targets, support, metrics = build_target_support(panel())
    small = targets.query("scope == 'smallest_20pct'")
    assert small.groupby('arm').size().to_dict() == {
        'benchmark': 6, 'exclude_high_turnover': 4, 'low_turnover': 2}
    assert small.groupby('arm').weight.sum().tolist() == pytest.approx([1, 1, 1])
    assert set(small.query("arm=='low_turnover'").symbol) == {'S04', 'S05'}
    assert support.query("scope=='smallest_20pct'").common_signal_count.iloc[0] == 6
    assert metrics.target_change_half_l1.isna().all()


def test_signal_missingness_is_counted_before_common_support_and_no_return_filter():
    p = panel()
    p.loc[0, 'signal_low_turnover'] = np.nan
    p['future_return'] = np.nan
    targets, support, _ = build_target_support(p)
    s = support.query("scope=='smallest_20pct'").iloc[0]
    assert s.original_cohort_count == 6 and s.common_signal_count == 5
    assert s.missing_signal_count == 1
    assert len(targets.query("scope=='smallest_20pct' and arm=='benchmark'")) == 5
    assert 'future_return' not in targets


def test_missing_exposure_is_unknown_without_changing_targets():
    p = panel()
    p.loc[5, 'lowvol_score'] = np.nan
    targets, _, metrics = build_target_support(p)
    m = metrics.query("scope=='smallest_20pct' and arm=='low_turnover'").iloc[0]
    assert np.isnan(m.lowvol_score_exposure)
    assert m.lowvol_score_coverage == pytest.approx(.5)
    assert len(targets.query("scope=='smallest_20pct' and arm=='low_turnover'")) == 2


def test_target_change_is_half_l1_and_gap_does_not_bridge():
    p = panel()
    second = p.copy()
    second.trade_date = '2020-02-28'
    second.signal_low_turnover = -second.signal_low_turnover
    targets, _, metrics = build_target_support(pd.concat([p, second]))
    m = metrics.query("scope=='smallest_20pct' and arm=='low_turnover'")
    assert m.target_change_half_l1.iloc[1] == pytest.approx(1)
    gap = p.copy()
    gap.trade_date = '2020-02-28'
    gap.signal_low_turnover = np.nan
    third = second.copy()
    third.trade_date = '2020-03-31'
    _, support, metrics = build_target_support(pd.concat([p, gap, third]))
    assert support.query("date=='2020-02-28'").status.eq('insufficient_support').all()
    assert metrics.query("date=='2020-03-31'").target_change_half_l1.isna().all()


def test_unknown_industry_and_invalid_keys():
    p = panel()
    p.loc[5, 'industry_l1'] = None
    _, _, m = build_target_support(p)
    row = m.query("scope=='smallest_20pct' and arm=='low_turnover'").iloc[0]
    assert row.industry_missing_weight == pytest.approx(.5)
    with pytest.raises(ValueError, match='duplicate'):
        build_target_support(pd.concat([p, p]))
    p.loc[0, 'size_score'] = np.inf
    with pytest.raises(ValueError, match='finite size'):
        build_target_support(p)
