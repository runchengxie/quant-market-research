"""Independent numerical and input-boundary checks for commodity research."""

import hashlib
import json

import pandas as pd
import pytest

from market_research.studies.commodity_equity.inputs import read_bundle, audit_pair
from market_research.studies.commodity_equity.analysis import (
    portfolio_path,
    summarize,
    monthly_levels,
    holding_summary,
)
from market_research.studies.commodity_equity.run import run_study


def test_portfolio_drifts_until_rebalance_and_uses_beginning_weights():
    dates = pd.to_datetime(["2020-12-31", "2021-01-29", "2021-02-26"])
    levels = pd.DataFrame({"equity": [100, 200, 100], "commodity": [100, 100, 200]}, index=dates)
    monthly = portfolio_path(levels, 0.2, "monthly", {dates[1], dates[2]})
    annual = portfolio_path(levels, 0.2, "annual", {dates[1], dates[2]})
    assert monthly.tolist() == pytest.approx([1, 1.8, 1.44])
    assert annual.tolist() == pytest.approx([1, 1.8, 1.2])
    dragged = portfolio_path(levels, 0.2, "monthly", set(dates), 100)
    years = (dates[-1] - dates[0]).days / 365.25
    assert dragged.iloc[-1] == pytest.approx(1.44 * 0.99**years)


def test_daily_drawdown_and_censored_recovery_use_real_dates():
    s = pd.Series(
        [100, 80, 100, 90],
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-10", "2020-01-20"]),
    )
    result = summarize(s)
    assert result["max_drawdown"] == pytest.approx(-0.2)
    assert result["drawdown_episodes"][0]["recovered"] is True
    assert result["drawdown_episodes"][0]["calendar_days"] == 9
    assert result["drawdown_episodes"][1]["recovered"] is False
    assert result["drawdown_episodes"][1]["calendar_days"] == 10
    assert result["cagr"] == pytest.approx(0.9 ** (365.25 / 19) - 1)


def test_month_end_requires_exact_endpoint_and_excludes_partial_last_month():
    calendar = pd.to_datetime(
        ["2020-12-31", "2021-01-04", "2021-01-29", "2021-02-01", "2021-02-26"]
    )
    s = pd.Series([100, 101, 103, 104], index=calendar[:-1])
    result = monthly_levels(s, calendar, pd.Timestamp("2021-02-10"))
    assert result.index.tolist() == pd.to_datetime(["2020-12-31", "2021-01-31"]).tolist()
    assert result.tolist() == [100, 103]
    with pytest.raises(ValueError, match="endpoint"):
        monthly_levels(s.drop(pd.Timestamp("2021-01-29")), calendar, pd.Timestamp("2021-02-10"))


def test_pair_audit_blocks_internal_gap_instead_of_silently_intersecting():
    days = pd.to_datetime(["2020-12-31", "2021-01-04", "2021-01-05"])
    eq = pd.Series([100, 101, 102], index=days)
    com = pd.Series([100, 102], index=days[[0, 2]])
    audit, aligned = audit_pair(eq, com, days, days, days[0], days[-1])
    assert audit["eligible"] is False
    assert audit["commodity_missing"] == ["2021-01-04"]
    assert aligned is None


def test_calendar_differences_are_reported_not_counted_as_missing_quotes():
    eq_days = pd.to_datetime(["2020-12-31", "2021-01-04", "2021-01-05"])
    com_days = eq_days[[0, 2]]
    eq = pd.Series([100, 101, 102], index=eq_days)
    com = pd.Series([100, 102], index=com_days)
    audit, aligned = audit_pair(eq, com, eq_days, com_days, eq_days[0], eq_days[-1])
    assert audit["eligible"] is True
    assert audit["equity_only_sessions"] == ["2021-01-04"]
    assert len(aligned) == 2


def bundle(tmp_path, items=None):
    payload = {
        "code": 0,
        "data": {
            "fields": ["ts_code", "trade_date", "close"],
            "items": items or [["X.NH", "20210104", 100], ["X.NH", "20210105", 101]],
        },
    }
    raw = json.dumps(payload).encode()
    (tmp_path / "x.json").write_bytes(raw)
    receipt = [
        {
            "id": "x",
            "api": "fut_index_daily",
            "params": {"ts_code": "X.NH"},
            "code": 0,
            "rows": len(payload["data"]["items"]),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    ]
    receipt_raw = json.dumps(receipt).encode()
    (tmp_path / "receipt.json").write_bytes(receipt_raw)
    manifest = {
        "schema_version": 1,
        "source_revision": "a" * 40,
        "sources": [
            {
                "receipt_path": str(tmp_path / "receipt.json"),
                "receipt_sha256": hashlib.sha256(receipt_raw).hexdigest(),
                "ids": ["x"],
            }
        ],
        "series": {
            "X.NH": {"currency": "CNY", "return_basis": "commodity_index", "role": "commodity"}
        },
    }
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(manifest))
    return p


def test_frozen_bundle_checks_hashes_and_rejects_mixed_identity(tmp_path):
    p = bundle(tmp_path)
    series, _, _ = read_bundle(p)
    assert series["X.NH"].tolist() == [100, 101]
    (tmp_path / "x.json").write_text("{}")
    with pytest.raises(ValueError, match="hash"):
        read_bundle(p)
    p = bundle(tmp_path, [["Y.NH", "20210104", 100]])
    with pytest.raises(ValueError, match="identity"):
        read_bundle(p)


@pytest.mark.parametrize(
    "items",
    [
        [["X.NH", "20210104", 100], ["X.NH", "20210104", 100]],
        [["X.NH", "20210104", 0]],
        [["X.NH", "20210104", None]],
    ],
)
def test_frozen_bundle_rejects_duplicate_or_invalid_levels(tmp_path, items):
    with pytest.raises(ValueError):
        read_bundle(bundle(tmp_path, items))


def test_runner_refuses_output_inside_repository_or_existing_directory(tmp_path):
    p = bundle(tmp_path)
    (tmp_path / ".git").mkdir()
    with pytest.raises(ValueError, match="outside"):
        run_study(p, tmp_path / "output")
    (tmp_path / ".git").rmdir()
    with pytest.raises(FileExistsError):
        run_study(p, tmp_path)


def test_holding_windows_do_not_bridge_missing_months_or_invent_long_history():
    dates = pd.date_range("2020-12-31", periods=13, freq="ME")
    values = pd.Series([100] * 12 + [90], index=dates)
    rows = holding_summary(values)
    assert rows[0]["completed_windows"] == 1
    assert rows[0]["worst_annualized_return"] == pytest.approx(-0.1)
    assert rows[1]["completed_windows"] == 0
    assert rows[1]["worst_annualized_return"] is None
    with pytest.raises(ValueError, match="consecutive"):
        holding_summary(values.drop(dates[4]))


def test_recent_periods_use_exact_calendar_endpoints_and_missing_history():
    from market_research.studies.commodity_equity.analysis import period_returns

    dates = pd.to_datetime(
        ["2025-11-06", "2025-12-31", "2026-09-30", "2026-10-23", "2026-10-30", "2026-11-06"]
    )
    s = pd.Series([100, 110, 120, 125, 130, 140], index=dates)
    result = period_returns(s, dates)
    assert result["last_week"]["start"] == "2026-10-30"
    assert result["last_week"]["return"] == pytest.approx(140 / 130 - 1)
    assert result["last_month"]["start"] == "2026-09-30"
    assert result["last_month"]["end"] == "2026-10-30"
    assert result["year_to_date"]["return"] == pytest.approx(140 / 110 - 1)
    assert result["trailing_12_months"]["return"] == pytest.approx(0.4)
    assert period_returns(s.iloc[1:], dates)["trailing_12_months"] is None


def complete_bundle(tmp_path):
    path = bundle(tmp_path)
    manifest = json.loads(path.read_text())
    rows = json.loads((tmp_path / "receipt.json").read_text())
    dates = ["20201231", "20210129", "20210226", "20210331"]
    payloads = {
        "eq": (
            "index_daily",
            {"ts_code": "E.CSI"},
            ["ts_code", "trade_date", "close"],
            [["E.CSI", d, 100 + i * 10] for i, d in enumerate(dates)],
        ),
        "co": (
            "fut_index_daily",
            {"ts_code": "X.NH"},
            ["ts_code", "trade_date", "close"],
            [["X.NH", d, 100] for d in dates],
        ),
        "sse": (
            "trade_cal",
            {"exchange": "SSE"},
            ["exchange", "cal_date", "is_open"],
            [["SSE", d, 1] for d in dates],
        ),
        "shfe": (
            "trade_cal",
            {"exchange": "SHFE"},
            ["exchange", "cal_date", "is_open"],
            [["SHFE", d, 1] for d in dates],
        ),
    }
    rows = []
    for name, (api, params, fields, items) in payloads.items():
        raw = json.dumps({"code": 0, "data": {"fields": fields, "items": items}}).encode()
        (tmp_path / (name + ".json")).write_bytes(raw)
        rows.append(
            {
                "id": name,
                "api": api,
                "params": params,
                "code": 0,
                "rows": len(items),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    raw = json.dumps(rows).encode()
    (tmp_path / "receipt.json").write_bytes(raw)
    manifest["sources"][0].update(
        receipt_sha256=hashlib.sha256(raw).hexdigest(), ids=list(payloads)
    )
    manifest.update(start="2020-12-31", end="2021-03-31")
    manifest["series"]["E.CSI"] = {
        "role": "equity",
        "currency": "CNY",
        "return_basis": "total_return",
    }
    path.write_text(json.dumps(manifest))
    return path


def test_runner_end_to_end_preserves_hypothetical_costs_and_unavailable_windows(tmp_path):
    path = complete_bundle(tmp_path)
    result = run_study(path, tmp_path / "result")
    pair = result["comparisons"]["E.CSI__X.NH"]
    assert pair["audit"]["eligible"] is True
    assert pair["analysis"]["daily"]["equity"]["total_return"] == pytest.approx(0.3)
    assert len(pair["analysis"]["allocation"]) == 30
    assert pair["analysis"]["holding_periods"]["commodity"][0]["completed_windows"] == 0
    assert pair["analysis"]["diversification"]["correlation"]["equity"]["commodity"] is None
    assert all(x["calibrated_cost"] is False for x in pair["analysis"]["allocation"])
    assert (
        json.loads((tmp_path / "result/result.json").read_text())["manifest_sha256"]
        == hashlib.sha256(path.read_bytes()).hexdigest()
    )


def test_runner_rejects_mislabeled_return_basis_before_analysis(tmp_path):
    path = complete_bundle(tmp_path)
    manifest = json.loads(path.read_text())
    manifest["series"]["E.CSI"]["return_basis"] = "adjusted_futures_price"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="return basis"):
        run_study(path, tmp_path / "result")


def test_verified_weekend_month_end_is_included_and_is_latest_completed_month():
    from market_research.studies.commodity_equity.analysis import period_returns

    calendar = pd.to_datetime(["2026-08-31", "2026-09-30", "2026-10-30", "2026-11-30"])
    values = pd.Series([100, 110, 121], index=calendar[:3])
    marks = monthly_levels(values, calendar, pd.Timestamp("2026-10-30"))
    assert len(marks) == 3
    assert marks.index[-1] == pd.Timestamp("2026-10-31")
    result = period_returns(values, calendar)
    assert result["last_month"]["start"] == "2026-09-30"
    assert result["last_month"]["end"] == "2026-10-30"
    assert result["last_month"]["return"] == pytest.approx(0.1)


def test_fixed_year_endpoint_uses_verified_prior_session_and_never_shortens_history():
    from market_research.studies.commodity_equity.analysis import period_returns

    calendar = pd.to_datetime(
        ["2015-12-31", "2020-12-31", "2022-12-30", "2025-12-31", "2026-01-30"]
    )
    values = pd.Series([100, 110, 120, 150], index=calendar[:4])
    result = period_returns(values, calendar)
    assert result["trailing_3_years"] == {
        "start": "2022-12-30",
        "end": "2025-12-31",
        "return": 0.25,
    }
    assert result["trailing_5_years"]["return"] == pytest.approx(150 / 110 - 1)
    assert result["trailing_10_years"]["return"] == pytest.approx(0.5)
    assert period_returns(values.iloc[1:], calendar)["trailing_10_years"] is None
