import importlib.util
import ast
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


path = Path(__file__).parents[1] / "scripts/analyze_grouped_valuation_controls.py"
spec = importlib.util.spec_from_file_location("controls", path)
mod = importlib.util.module_from_spec(spec)
if path.exists():
    spec.loader.exec_module(mod)


def frame():
    rows = []
    for q, count, value in [(1, 10, 0.2), (2, 5, 0.1)]:
        for i in range(count):
            rows.append(dict(symbol=f"{q}-{i}", quintile=q, reporting_group="general_reporting",
                             size_bucket=1, profitability_bucket=2, outcome=value,
                             common_five=True, same_report_period=True))
    return pd.DataFrame(rows)


def test_support_is_outcome_independent_and_does_not_drop_failed_buys():
    a = frame()
    a.loc[0, "outcome"] = 0.0
    first = mod.match_support(a, ["reporting_group", "size_bucket"], 2, 5)
    a.loc[0, "outcome"] = np.nan
    second = mod.match_support(a, ["reporting_group", "size_bucket"], 2, 5)
    assert len(first) == 15
    pd.testing.assert_series_equal(first.match_weight, second.match_weight)
    with pytest.raises(ValueError, match="outcome"):
        mod.match_support(a, ["outcome"], 2, 5)


def test_target_weights_use_q1_distribution_and_unknown_strict_is_not_zero():
    a = frame()
    other = frame()
    other["size_bucket"] = 2
    other = other.loc[~(other.quintile.eq(1) & other.index.isin(range(5)))]
    a = pd.concat([a, other], ignore_index=True)
    support = mod.match_support(a, ["reporting_group", "size_bucket"], 2, 5)
    assert support.loc[support.quintile.eq(1), "match_weight"].sum() == pytest.approx(1)
    assert support.loc[support.quintile.eq(2), "match_weight"].sum() == pytest.approx(1)
    assert support.loc[support.size_bucket.eq(1) & support.quintile.eq(2), "match_weight"].sum() == pytest.approx(2 / 3)
    result = mod.estimate(support, "outcome", 2, weighted=True)
    assert result["contrast"] == pytest.approx(0.1)
    support.loc[0, "outcome"] = np.nan
    result = mod.estimate(support, "outcome", 2, weighted=True)
    assert result["contrast"] is None
    assert result["q1_unknown"] == 1


def test_insufficient_support_and_feature_missing_remain_unavailable():
    a = frame()
    a.loc[a.quintile.eq(2), "profitability_bucket"] = np.nan
    assert mod.match_support(a, mod.PRIMARY_FEATURES, 2, 5).empty
    assert mod.match_support(frame(), mod.PRIMARY_FEATURES, 2, 6).empty
    assert mod.estimate(a.iloc[:0], "outcome", 2)["contrast"] is None
    a = frame()
    a["reporting_group"] = "unknown"
    assert mod.match_support(a, mod.PRIMARY_FEATURES, 2, 5).empty


def test_common_sample_preserves_original_quintiles():
    a = frame()
    a.loc[0, "common_five"] = False
    a.loc[1, "same_report_period"] = False
    common = mod.common_sample(a)
    assert len(common) == 13
    pd.testing.assert_series_equal(common.quintile, a.loc[common.index, "quintile"])


def test_bootstrap_keeps_missing_month_schedule_and_is_deterministic():
    dates = ["20230131", "20230331"]
    schedule = mod.month_schedule(dates)
    assert schedule == ["202301", "202302", "202303"]
    series = pd.Series([1.0, np.nan, 3.0], index=schedule)
    assert mod.block_bootstrap(series, minimum=12)["status"] == "insufficient_supported_months"
    s = pd.Series(np.arange(18, dtype=float))
    s.iloc[5] = np.nan
    assert mod.block_bootstrap(s) == mod.block_bootstrap(s)
    b = mod.block_bootstrap(s)
    assert b["valid_replications"] + b["invalid_replications"] == 2000
    assert b["supported_month_range"] == ["0", "17"]


def test_bootstrap_resamples_original_missing_slots_before_finite_mean():
    values = np.array([np.nan] * 24 + list(np.arange(12, dtype=float)))
    result = mod.block_bootstrap(pd.Series(values), replications=2000)
    starts = np.random.default_rng(20261021).integers(0, 36, size=(2000, 12))
    index = ((starts[:, :, None] + np.arange(3)) % 36).reshape(2000, 36)
    sampled = values[index]
    good = np.isfinite(sampled)
    counts = good.sum(axis=1)
    finite = counts > 0
    means = np.where(good, sampled, 0).sum(axis=1)[finite] / counts[finite]
    assert result["low"] == pytest.approx(np.quantile(means, .025))
    assert result["high"] == pytest.approx(np.quantile(means, .975))
    assert result["invalid_replications"] == int((~finite).sum())
    assert result["supported_month_range"] == ["24", "35"]


def test_quality_requires_same_period_and_positive_ordinary_is_not_assumed():
    a = pd.DataFrame(dict(income_period=["20231231"] * 4,
                          fina_indicator_period=["20231231", "20230930", "20231231", "20231231"],
                          denominator_pe_ttm=[10, 10, -1, 10],
                          denominator_pe_deducted_proxy=[4, 8, 2, np.nan]))
    assert mod.quality_labels(a).tolist() == ["deducted_share_lt_0.5", None, "ordinary_nonpositive", None]
    a.loc[2, "denominator_pe_deducted_proxy"] = np.nan
    assert mod.quality_labels(a).iloc[2] == "ordinary_nonpositive"


def test_leverage_requires_prior_announcement_matching_period_and_freshness():
    panel = pd.DataFrame(dict(ts_code=["A", "B", "C"], formation_date=["20240430"] * 3,
                              balancesheet_period=["20231231"] * 3,
                              report_age_days=[121] * 3, reporting_group=["general_reporting"] * 3))
    bs = pd.DataFrame(dict(ts_code=["A", "B", "C"], end_date=["20231231"] * 3,
                           ann_date=["20240429", "20240430", "20240420"],
                           f_ann_date=["20240429", "20240430", "20240501"],
                           report_type=["1"] * 3, _source_retrieved_at=["2026-10-18T00:00:00Z"] * 3,
                           total_assets=[10] * 3, total_liab=[6] * 3))
    result = mod.attach_disclosure_features(panel, {"balancesheet": bs})
    assert result.leverage_bucket.tolist() == ["liabilities_to_assets_0.5_to_1", None, None]


def test_member_join_uses_entry_date_not_cohort_as_formation_date():
    m = pd.DataFrame(dict(ts_code=["A"], group=["all_market"], metric=["pb_parent"],
                          quintile=[1], entry_date=["20230103"], formation_date=["20221230"]))
    o = pd.DataFrame(dict(symbol=["A"], metric=["pb_parent"], quintile=[1],
                          entry_date=["20230103"], formation_date=["20221230"], scenario=["touch10"]))
    assert mod.join_members(m, o).formation_date.item() == "20221230"
    o["formation_date"] = "20230103"
    with pytest.raises(ValueError, match="formation"):
        mod.join_members(m, o)


def test_receipt_lineage_accepts_relative_runpy_filename(monkeypatch):
    repo = Path(__file__).parents[1].resolve()
    monkeypatch.chdir(repo)
    tree = ast.parse((repo / "scripts/analyze_grouped_valuation_controls.py").read_text())
    expression = next(n for n in ast.walk(tree) if isinstance(n, ast.DictComp)
                      and "relative_to(repo)" in ast.unparse(n))
    hashes = eval(compile(ast.Expression(expression), "source_lineage", "eval"),
                  {"repo": repo, "Path": Path, "__file__": "scripts/analyze_grouped_valuation_controls.py",
                   "digest": mod.digest})
    assert "scripts/analyze_grouped_valuation_controls.py" in hashes
    assert len(hashes["scripts/analyze_grouped_valuation_controls.py"]) == 64


def test_stability_separates_supported_mean_from_full_schedule_mean():
    p = pd.DataFrame([dict(metric="pb_parent", comparison_quintile=2, primary_contrast=True,
                          sample_basis="all_frozen", layer="report_size", stage="overlap", outcome="strict",
                          formation_month=m, contrast=v, q1_retention=1, comparison_retention=1,
                          q1_n=5, comparison_n=5, q1_unknown=int(pd.isna(v)), comparison_unknown=0)
                      for m, v in [("202212", .1), ("202301", np.nan), ("202302", .3)]])
    r = mod.stability(p, ["202212", "202301", "202302"])[0]
    assert r["full_schedule_complete"] is False
    assert r["full_schedule_mean_contrast"] is None
    assert r["supported_month_mean_contrast"] == pytest.approx(.2)
    assert r["missing_months"] == ["202301"]
    assert r["yearly"][0]["full_schedule_complete"] is True
    assert r["yearly"][0]["full_schedule_mean_contrast"] == pytest.approx(.1)
    assert r["yearly"][1]["full_schedule_mean_contrast"] is None
    assert r["yearly"][1]["missing_months"] == ["202301"]
