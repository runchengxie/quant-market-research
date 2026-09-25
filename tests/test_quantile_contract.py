import json

import numpy as np
import pandas as pd
import pytest

from market_research.barra import analyze_size_monotonicity
from market_research.style_portfolios import (
    analyze_tail_monotonicity,
    build_quantile_returns,
    summarize_market_factor_evidence,
)


def panel(n=10, periods=2):
    return pd.DataFrame([
        {
            "symbol": f"S{i:02}", "date": date, "market_cap": float(i + 1),
            "adj_close": 100 * (1 + i / 100) ** t,
        }
        for t, date in enumerate(pd.date_range("2024-01-01", periods=periods))
        for i in range(n)
    ])


def test_a_share_formation_requires_explicit_eligibility_evidence():
    frame = panel(4)
    frame["market"] = "a_share"
    with pytest.raises(ValueError, match="eligibility"):
        build_quantile_returns(frame, "market_cap", quantiles=2)

    frame["is_tradable"] = True
    frame["is_st"] = False
    frame["is_suspended"] = False
    result = build_quantile_returns(frame, "market_cap", quantiles=2)
    assert result["count"].sum() == 4


def build(frame, entrypoint, quantiles=5, holding_period=1):
    if entrypoint == "barra":
        return analyze_size_monotonicity(frame, quantiles, holding_period)[0]
    return build_quantile_returns(frame, "market_cap", quantiles, holding_period)


@pytest.mark.parametrize("n, expected", [
    (10, [2, 2, 2, 2, 2]), (11, [2, 2, 2, 2, 3]), (3, [1, 1, 1]),
])
def test_entrypoints_share_balanced_labels_and_symbol_tie_order(n, expected):
    frame = panel(n)
    frame["market_cap"] = 1.0
    first = build(frame.sample(frac=1, random_state=12), "barra")
    second = build(frame.sample(frac=1, random_state=44), "style")
    pd.testing.assert_frame_equal(first, second)
    assert first["count"].tolist() == expected
    # One-based ordinal ranks use integer ceiling; undersized samples leave gaps.
    labels = ((np.arange(1, n + 1) * 5 + n - 1) // n)
    for bucket, group in first.groupby("bucket"):
        assert group["mean_forward_return"].item() == pytest.approx(
            np.arange(n)[labels == bucket].mean() / 100
        )


@pytest.mark.parametrize("entrypoint", ["barra", "style"])
def test_duplicate_symbol_date_rejected_even_if_ineligible(entrypoint):
    frame = panel()
    duplicate = frame.iloc[[0]].assign(is_st=True)
    frame["is_st"] = False
    with pytest.raises(ValueError, match="duplicate.*symbol.*date"):
        build(pd.concat([frame, duplicate], ignore_index=True), entrypoint)


@pytest.mark.parametrize("entrypoint", ["barra", "style"])
def test_future_missingness_does_not_change_formation_groups(entrypoint):
    frame = panel()
    complete = build(frame, entrypoint)
    frame = frame.loc[~((frame.symbol == "S00") & (frame.date == "2024-01-02"))]
    result = build(frame, entrypoint)
    assert result["count"].tolist() == complete["count"].tolist()
    first = result.iloc[0]
    assert first["count"] == 2
    assert first["observed_return_count"] == 1
    assert first["missing_return_count"] == 1
    assert first["return_coverage"] == 0.5
    assert pd.isna(first["mean_forward_return"])
    assert pd.isna(first["median_forward_return"])
    assert first["observed_only_mean_forward_return"] == pytest.approx(0.01)
    assert first["observed_only_median_forward_return"] == pytest.approx(0.01)
    assert result.iloc[1:]["mean_forward_return"].tolist() == pytest.approx(
        complete.iloc[1:]["mean_forward_return"].tolist()
    )


@pytest.mark.parametrize("entrypoint", ["barra", "style"])
def test_target_uses_global_calendar_even_with_intermediate_symbol_gap(entrypoint):
    frame = panel(4, 4)
    frame = frame.loc[~((frame.symbol == "S01") & (frame.date == "2024-01-02"))]
    result = build(frame, entrypoint, quantiles=2, holding_period=2)
    first = result.loc[result.formation_date == "2024-01-01"].iloc[0]
    assert first["count"] == 2
    assert first["observed_return_count"] == 2
    assert first["mean_forward_return"] == pytest.approx((1.01**2 - 1) / 2)
    assert first["target_date"] == pd.Timestamp("2024-01-03")
    assert result.formation_date.max() == pd.Timestamp("2024-01-02")


@pytest.mark.parametrize("entrypoint", ["barra", "style"])
def test_missing_target_does_not_skip_to_later_symbol_quote(entrypoint):
    frame = panel(4, 4)
    frame = frame.loc[~((frame.symbol == "S01") & (frame.date == "2024-01-03"))]
    result = build(frame, entrypoint, quantiles=2, holding_period=2)
    first = result.loc[result.formation_date == "2024-01-01"].iloc[0]
    assert first["count"] == 2
    assert first["missing_return_count"] == 1
    assert pd.isna(first["mean_forward_return"])


@pytest.mark.parametrize("entrypoint", ["barra", "style"])
@pytest.mark.parametrize("bad", [np.inf, -np.inf, np.nan, 0, -1, "bad"])
def test_invalid_target_prices_count_as_missing(entrypoint, bad):
    frame = panel(4)
    frame["adj_close"] = frame.adj_close.astype(object)
    frame.loc[(frame.symbol == "S00") & (frame.date == "2024-01-02"), "adj_close"] = bad
    result = build(frame, entrypoint, quantiles=2)
    assert result["count"].sum() == 4
    assert result["missing_return_count"].sum() == 1
    assert pd.isna(result.iloc[0]["mean_forward_return"])


@pytest.mark.parametrize("entrypoint", ["barra", "style"])
def test_formation_rejects_nonfinite_numeric_values(entrypoint):
    frame = panel(6)
    frame.loc[frame.symbol == "S00", "market_cap"] = np.inf
    frame.loc[frame.symbol == "S01", "market_cap"] = -np.inf
    frame.loc[frame.symbol == "S02", "adj_close"] = np.inf
    frame.loc[frame.symbol == "S03", "adj_close"] = 0
    result = build(frame, entrypoint, quantiles=2)
    assert result["count"].sum() == 2
    assert result["return_coverage"].eq(1).all()


def test_signed_generic_factors_allowed_but_market_cap_must_be_positive():
    frame = panel(4)
    frame["market_cap"] = frame.market_cap - 2
    assert build(frame, "style", quantiles=2)["count"].sum() == 4
    assert build(frame, "barra", quantiles=2)["count"].sum() == 2


def test_custom_columns_use_same_calendar_and_validation():
    frame = panel(4).rename(columns={"date": "as_of", "adj_close": "price"})
    rows = build_quantile_returns(
        frame, "market_cap", quantiles=2, date_column="as_of", return_column="price"
    )
    assert rows["count"].sum() == 4
    assert rows["target_date"].eq(pd.Timestamp("2024-01-02")).all()


def diagnostic_rows(values):
    return pd.DataFrame(values, columns=["formation_date", "bucket", "mean_forward_return"])


@pytest.mark.parametrize("rows, tail", [
    ([], 1), ([("a", 1, 0.1)], 1),
    ([("a", 1, 0.1), ("a", 2, 0.2), ("a", 3, 0.3)], 2),
    ([("a", 1, 0.1), ("b", 2, 0.2)], 1),
    ([("a", 1, np.inf), ("a", 2, 0.2)], 1),
])
def test_insufficient_or_unpaired_diagnostics_are_unavailable(rows, tail):
    result = analyze_tail_monotonicity(diagnostic_rows(rows), tail_quantiles=tail)
    assert result["status"] == "unavailable"
    assert result["monotonicity_score"] is None
    assert result["tail_spread"] is None
    assert result["observations"] == 0
    json.dumps(result, allow_nan=False)


def test_diagnostic_curve_and_tails_use_only_common_complete_dates():
    rows = diagnostic_rows([
        ("a", 1, 0.1), ("a", 2, 0.2),
        ("b", 1, 9.0), ("c", 2, -9.0),
    ])
    result = analyze_tail_monotonicity(rows)
    assert result["status"] == "available"
    assert result["tail_spread"] == pytest.approx(-0.1)
    assert result["monotonicity_score"] == 1.0
    assert result["observations"] == 1
    assert result["formation_dates"] == 3
    assert result["warnings"]
    reverse = analyze_tail_monotonicity(rows, direction="descending")
    assert reverse["tail_spread"] == pytest.approx(0.1)
    assert reverse["monotonicity_score"] == 0.0


def test_diagnostics_reject_duplicate_date_bucket():
    rows = diagnostic_rows([("a", 1, 0.1), ("a", 1, 0.2), ("a", 2, 0.3)])
    with pytest.raises(ValueError, match="duplicate"):
        analyze_tail_monotonicity(rows)


def test_diagnostics_do_not_accept_partial_portfolio_mean_from_legacy_caller():
    rows = diagnostic_rows([("a", 1, 0.1), ("a", 2, 0.2)])
    rows["count"] = 2
    rows["observed_return_count"] = [1, 2]
    result = analyze_tail_monotonicity(rows)
    assert result["status"] == "unavailable"
    assert "missing_return_coverage" in result["warnings"]


def test_small_cross_section_does_not_claim_requested_quantiles_are_available():
    rows, summary = analyze_size_monotonicity(panel(3), quantiles=5)
    assert rows["bucket"].tolist() == [2, 4, 5]
    assert summary["status"] == "unavailable"
    assert summary["quantiles"] == 5
    assert summary["tail_spread"] is None
    assert analyze_tail_monotonicity(rows)["status"] == "unavailable"


def test_barra_missing_coverage_and_global_horizon_accounting():
    frame = panel(4)
    frame = frame.loc[~((frame.symbol == "S00") & (frame.date == "2024-01-02"))]
    _, summary = analyze_size_monotonicity(frame, quantiles=2)
    assert summary["eligible_rows"] == 4
    assert summary["observed_return_count"] == 3
    assert summary["missing_return_count"] == 1
    assert summary["return_coverage"] == 0.75
    assert summary["unavailable_target_rows"] == 3
    assert summary["status"] == "unavailable"
    assert summary["tail_spread"] is None
    assert "missing_return_coverage" in summary["warnings"]
    json.dumps(summary, allow_nan=False)


@pytest.mark.parametrize("frame", [panel(4, 1), panel(0)])
def test_empty_barra_and_factor_evidence_are_unavailable(frame):
    if frame.empty:
        frame = panel(4).iloc[:0]
    rows, summary = analyze_size_monotonicity(frame, quantiles=2)
    assert rows.empty
    assert summary["status"] == "unavailable"
    assert summary["monotonicity_score"] is None
    assert summary["tail_spread"] is None
    assert summary["return_coverage"] is None
    evidence = summarize_market_factor_evidence(rows, "size", {"source": "test"})
    assert evidence["evidence_status"] == "unavailable"
    assert evidence["provenance"] == {"source": "test"}
    json.dumps(summary, allow_nan=False)
