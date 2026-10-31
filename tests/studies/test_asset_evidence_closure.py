import pandas as pd
import pytest

from market_research.studies.asset_returns.closure import annual_etf_audit, classify_member
from market_research.studies.asset_returns.release import validate_update


def test_annual_nav_audit_has_complete_year_and_rounded_report_check():
    dates = pd.date_range("2018-12-31", "2020-12-31", freq="ME")
    frame = pd.DataFrame(
        {
            "date": dates,
            "adj_nav": [1.1 ** (i / 12) for i in range(25)],
            "index_total": [1.05 ** (i / 12) for i in range(25)],
        }
    )
    result = annual_etf_audit(frame, {2019: 0.10, 2020: 0.10})
    assert len(result) == 2
    assert all(r["disclosed_return_matches"] for r in result)
    assert result[0]["relative_wealth_change"] == pytest.approx(1.1 / 1.05 - 1)
    with pytest.raises(ValueError, match="monthly"):
        annual_etf_audit(frame.drop(index=4), {})


def test_identity_status_does_not_invent_profit_or_merger_successor():
    assert (
        classify_member({"list_status": "D", "delist_date": "20250801"}, False)
        == "delisted_by_fiscal_end"
    )
    assert (
        classify_member({"list_status": "D", "delist_date": "20260801"}, False)
        == "delisted_after_fiscal_end"
    )
    assert classify_member({"list_status": "L"}, False) == "listed_missing_profit"
    assert classify_member(None, False) == "unresolved_identity"
    assert classify_member({"list_status": "D"}, True) == "profit_retrieved_requires_vintage_review"


def test_release_rejects_history_revisions_currency_and_cost_basis():
    old = pd.DataFrame({"date": ["2025-01-31", "2025-02-28"], "equity": [100.0, 101.0]})
    new = pd.concat(
        [old, pd.DataFrame({"date": ["2025-03-31"], "equity": [102.0]})], ignore_index=True
    )
    metadata = {
        "currency": "CNY",
        "return_basis": "total_return",
        "cost_basis": "per_traded_notional",
    }
    assert validate_update(old, new, metadata, metadata)["appended_months"] == 1
    revised = new.copy()
    revised.loc[0, "equity"] = 99.0
    with pytest.raises(ValueError, match="history"):
        validate_update(old, revised, metadata, metadata)
    with pytest.raises(ValueError, match="cost_basis"):
        validate_update(old, new, metadata, {**metadata, "cost_basis": "annual_wealth_drag"})
    with pytest.raises(ValueError, match="currency"):
        validate_update(old, new, metadata, {**metadata, "currency": "USD"})
    with pytest.raises(ValueError, match="finite"):
        validate_update(old, new.assign(equity=float("nan")), metadata, metadata)


@pytest.mark.parametrize(
    "dates",
    [
        ["2025-01-31", "2025-01-31"],
        ["2025-01-31", "2025-03-31"],
        ["2025-02-28", "2025-01-31"],
    ],
)
def test_monthly_gate_rejects_duplicate_missing_or_reversed_months(dates):
    old = pd.DataFrame({"date": ["2025-01-31"], "equity": [100.0]})
    candidate = pd.DataFrame({"date": dates, "equity": [100.0, 101.0]})
    contract = {"currency": "CNY", "return_basis": "total_return", "cost_basis": "none"}
    with pytest.raises(ValueError, match="monthly"):
        validate_update(old, candidate, contract, contract)
