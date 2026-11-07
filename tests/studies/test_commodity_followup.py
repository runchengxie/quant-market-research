"""Numerical regressions for the four follow-up research lines."""

import pandas as pd
import pytest

from market_research.studies.commodity_equity.robustness import (
    index_account,
    rolling_comparison,
    annual_drag_budget,
)
from market_research.studies.commodity_equity.implementation import (
    collateral_levels,
    fund_comparison,
)
from market_research.studies.commodity_equity.regimes import classify_regimes


def test_account_drift_and_funded_costs_exclude_initial_and_final_trades():
    dates = pd.to_datetime(["2020-12-31", "2021-01-29", "2021-02-26"])
    levels = pd.DataFrame({"equity": [100, 200, 100], "commodity": [100, 100, 200]}, index=dates)
    gross = index_account(levels, 0.2, "monthly", set(dates))
    assert gross["nav"].tolist() == pytest.approx([1, 1.8, 1.44])
    annual = index_account(levels, 0.2, "annual", set(dates))
    assert annual["nav"].tolist() == pytest.approx([1, 1.8, 1.2])
    net = index_account(levels, 0.2, "monthly", set(dates), 100)
    fee = 0.0032 / 0.994
    assert net["cost_paid"] == pytest.approx(fee)
    assert net["rebalance_count"] == 1
    assert net["nav"].iloc[-1] == pytest.approx((1.8 - fee) * 0.8)


def test_rolling_windows_reset_initial_weights_and_reject_missing_months():
    dates = pd.date_range("2020-12-31", periods=4, freq="ME")
    levels = pd.DataFrame(
        {"equity": [100, 200, 100, 150], "commodity": [100, 100, 200, 100]}, index=dates
    )
    rows = rolling_comparison(levels, pd.DatetimeIndex(dates), 0.2, "annual", horizon_months=2)
    assert len(rows) == 2
    assert rows[0]["portfolio_total_return"] == pytest.approx(0.2)
    # A slice of the first global path would inherit drift, not fresh 80/20 weights.
    assert rows[1]["portfolio_total_return"] == pytest.approx(-0.2)
    with pytest.raises(ValueError, match="consecutive"):
        rolling_comparison(levels.drop(dates[1]), dates.delete(1), 0.2, "monthly", 2)


def test_annual_extra_drag_budget_is_geometric_and_no_positive_budget_for_loser():
    assert annual_drag_budget(1.1, 1.05, 1) == pytest.approx((1 - 1.05 / 1.1) * 10000)
    assert annual_drag_budget(1.01, 1.05, 1) == 0
    assert annual_drag_budget(1.1**5, 1.05**5, 5) == pytest.approx((1 - 1.05 / 1.1) * 10000)


def test_collateral_uses_only_prior_available_rate_and_adds_income_once():
    dates = pd.to_datetime(["2020-12-31", "2021-01-04", "2021-01-05"])
    commodity = pd.Series([100, 101, 102], index=dates)
    rates = pd.Series([3.65, 100], index=pd.to_datetime(["2020-12-31", "2021-01-05"]))
    result = collateral_levels(commodity, rates, 1)
    expected = (1 + 0.01 + 0.0365 * 4 / 365) * (1 + 102 / 101 - 1 + 0.0365 / 365)
    assert result.iloc[-1] / result.iloc[0] == pytest.approx(expected)
    with pytest.raises(ValueError, match="already"):
        collateral_levels(commodity, rates, 1, already_includes_cash=True)


def test_macro_publication_guard_separates_release_timing_from_known_vintage():
    decisions = pd.to_datetime(["2025-01-31", "2025-02-28"])
    records = pd.DataFrame(
        [
            {"series": "pmi", "available_at": "2025-01-01", "value": 49, "vintage_verified": True},
            {"series": "ppi", "available_at": "2025-01-10", "value": -2, "vintage_verified": True},
            {"series": "pmi", "available_at": "2025-02-01", "value": 51, "vintage_verified": False},
            {"series": "ppi", "available_at": "2025-03-01", "value": 3, "vintage_verified": True},
        ]
    )
    strict = classify_regimes(decisions, records, require_verified=True)
    diagnostic = classify_regimes(decisions, records, require_verified=False)
    assert strict[0]["regime"] == "pmi_below_50__ppi_below_0"
    assert strict[1]["regime"] == "pmi_below_50__ppi_below_0"
    assert diagnostic[1]["regime"] == "pmi_at_least_50__ppi_below_0"
    assert diagnostic[1]["point_in_time_verified"] is False


def test_product_comparison_never_calls_unmatched_sector_index_tracking_error():
    dates = pd.date_range("2020-12-31", periods=3, freq="ME")
    levels = pd.DataFrame(
        {
            "close": [1, 1.1, 1.2],
            "adj_factor": [1, 1, 1],
            "unit_nav": [1, 1.05, 1.1],
            "adj_nav": [1, 1.05, 1.1],
        },
        index=dates,
    )
    result = fund_comparison(levels, "sector ETF", "Issuer exchange index", "NHCI.NH")
    assert result["same_benchmark"] is False
    assert result["tracking_error"] is None
    assert result["manager_fees_subtracted_again"] is False
    assert result["market_total_return_proxy"] == pytest.approx(0.2)


def test_event_reconstruction_excludes_caixin_and_nonmanufacturing_and_retains_vintage_limit():
    from market_research.studies.commodity_equity.followup_inputs import event_records

    events = pd.DataFrame(
        [
            {
                "date": "20250131",
                "country": "中国",
                "event": "中国官方制造业PMI(一月)",
                "value": "49.1",
            },
            {
                "date": "20250131",
                "country": "中国",
                "event": "中国官方非制造业PMI(一月)",
                "value": "50.2",
            },
            {
                "date": "20250131",
                "country": "中国",
                "event": "中国财新制造业PMI(一月)",
                "value": "50.1",
            },
            {
                "date": "20250209",
                "country": "中国",
                "event": "中国PPI年率(%)(一月)",
                "value": "-2.3%",
            },
        ]
    )
    result = event_records(events)
    assert len(result) == 2
    assert result.iloc[0]["available_at"] == "2025-02-01T00:00:00"
    assert result.iloc[1]["value"] == -2.3
    assert not result["vintage_verified"].any()


def test_frozen_exports_reject_tampered_response_and_calendar_caps(tmp_path):
    import json
    import hashlib
    from market_research.studies.commodity_equity.followup_inputs import read_exports

    raw = json.dumps({"code": 0, "data": {"fields": ["event"], "items": [["x"]] * 100}}).encode()
    (tmp_path / "x.json").write_bytes(raw)
    receipt = json.dumps(
        [
            {
                "id": "x",
                "api": "eco_cal",
                "params": {},
                "code": 0,
                "rows": 100,
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        ]
    ).encode()
    p = tmp_path / "receipt.json"
    p.write_bytes(receipt)
    sources = [{"receipt_path": str(p), "receipt_sha256": hashlib.sha256(receipt).hexdigest()}]
    with pytest.raises(ValueError, match="capped"):
        read_exports(sources)
    (tmp_path / "x.json").write_text("{}")
    with pytest.raises(ValueError, match="hash"):
        read_exports(sources)


def test_followup_runner_refuses_repository_outputs_and_changed_manifest(tmp_path):
    import json
    from market_research.studies.commodity_equity.followup_run import run_followup

    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "baseline_manifest_path": str(tmp_path / "base.json"),
                "baseline_manifest_sha256": "0" * 64,
            }
        )
    )
    (tmp_path / ".git").mkdir()
    with pytest.raises(ValueError, match="outside"):
        run_followup(path, tmp_path / "out")
    (tmp_path / ".git").rmdir()
    (tmp_path / "base.json").write_text("{}")
    with pytest.raises(ValueError, match="hash"):
        run_followup(path, tmp_path / "out")
