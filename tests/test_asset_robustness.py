import numpy as np
import pandas as pd
import pytest

from market_research.studies.asset_returns.robustness import (
    endpoint_sensitivity,
    annual_contributions,
    relative_waiting,
)


def frame(values, start="2019-12-31", **extra):
    return pd.DataFrame(
        {"date": pd.date_range(start, periods=len(values), freq="ME"), "total": values, **extra}
    )


def test_endpoint_sensitivity_uses_actual_time_and_sorts_input():
    f = frame(100 * 1.01 ** np.arange(73))
    r = endpoint_sensitivity(f.iloc[::-1], "total", minimum_months=60)
    assert r["cells"]
    assert all(c["months"] >= 60 for c in r["cells"])
    assert all(c["cagr"] == pytest.approx(1.01**12 - 1) for c in r["cells"])
    assert r["fixed_start_endpoints"][-1]["end"] == "2025-12-31"
    with pytest.raises(ValueError):
        endpoint_sensitivity(f.iloc[[0, 2]], "total")


def test_annual_log_contributions_reconcile_with_a_negative_year():
    f = frame(np.r_[100, np.linspace(100, 200, 12), np.linspace(200, 100, 12)])
    r = annual_contributions(f, "total")
    assert [row["year"] for row in r["years"]] == [2020, 2021]
    assert r["years"][0]["return"] == pytest.approx(1)
    assert r["years"][1]["return"] == pytest.approx(-0.5)
    assert sum(row["log_growth"] for row in r["years"]) == pytest.approx(0)
    assert r["total_log_growth"] == pytest.approx(0)
    assert all(row["share_of_total_log_growth"] is None for row in r["years"])


def test_relative_waits_retain_censoring_and_use_months():
    f = frame([100, 90, 95, 105, 90], benchmark=[100] * 5)
    r = relative_waiting(f, "total", "benchmark")
    assert r["longest_observed_underperformance_months"] == 3
    assert r["episodes"][0]["recovery_date"] == "2020-03-31"
    assert r["episodes"][0]["months"] == 3
    assert r["episodes"][1]["censored"] is True
    assert r["episodes"][1]["months"] == 1
    assert r["no_followup_entries"] == 1
    assert r["followed_entries"] == 4
