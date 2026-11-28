import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location(
    'breadth', Path(__file__).parents[1] / 'scripts/explore_smallcap_style_breadth.py')
breadth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(breadth)


def panel():
    p = pd.DataFrame({'trade_date': ['2020-01-31'] * 10,
                      'symbol': [str(i) for i in range(10)], 'industry_l1': ['A'] * 10})
    for f in breadth.FACTORS + breadth.SIGNALS:
        p[f] = np.arange(10, dtype=float)
    return p


def test_equal_weight_and_rank_orientation_with_shortfall():
    detail, _, _, _ = breadth.explore(panel(), [3])
    eq = detail.query("scope == 'all' and gamma == 0").iloc[0]
    ranked = detail.query("scope == 'all' and gamma == 0.5").iloc[0]
    assert eq.effective_holdings == pytest.approx(3)
    assert ranked.effective_holdings < 3
    assert ranked.size_score_vs_all > eq.size_score_vs_all
    small = detail.query("scope == 'smallest_20pct'")
    assert (small.selected_count == 2).all()
    assert small.shortfall.all()
    assert small.size_score_vs_all.max() < 0


def test_missing_factor_does_not_renormalize_exposure():
    p = panel()
    p.loc[9, 'activity_20d_score'] = np.nan
    detail, _, _, _ = breadth.explore(p, [3])
    row = detail.query("scope == 'all' and gamma == 0").iloc[0]
    assert row.activity_20d_score_coverage == pytest.approx(2 / 3)
    assert np.isnan(row.activity_20d_score_vs_all)


def test_duplicate_and_infinite_scores_fail():
    p = panel()
    with pytest.raises(ValueError, match='duplicate'):
        breadth.explore(pd.concat([p, p]), [3])
    p.loc[0, 'size_score'] = np.inf
    with pytest.raises(ValueError, match='infinite'):
        breadth.explore(p, [3])


def test_unknown_industry_is_retained():
    p = panel()
    p.loc[9, 'industry_l1'] = None
    detail, _, _, _ = breadth.explore(p, [3])
    row = detail.query("scope == 'all' and gamma == 0").iloc[0]
    assert row.industry_missing_weight == pytest.approx(1 / 3)
    assert row.industry_hhi == pytest.approx(5 / 9)


def test_comparison_uses_common_signal_dates():
    p = panel()
    earlier = p.copy()
    earlier.trade_date = '2019-12-31'
    earlier[breadth.SIGNALS[1]] = np.nan
    detail, summary, corr, _ = breadth.explore(pd.concat([earlier, p]), [3])
    assert detail.date.nunique() == 1
    assert summary.formation_dates.eq(1).all()
    assert corr.valid_dates.eq(1).all()
