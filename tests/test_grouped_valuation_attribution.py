from copy import deepcopy

import pandas as pd
import pytest

from scripts.decompose_grouped_valuation import (
    INITIAL, attribute_portfolio, cash_exposure, select_cases,
)
from market_research.studies.grouped_valuation_ledger import run_ledger


HOLDING_COLUMNS = ["date", "lot_id", "symbol", "cohort", "units", "marked_value"]
TERMINAL_COLUMNS = ["lot_id", "symbol", "cohort", "units", "terminal_date", "valuation_class",
                    "reference_value", "last_valid_date", "last_valid_price", "current_marked_value"]


def quote(price):
    return dict(adj_close=price, amount=100, is_suspended=False, is_limit_up=False,
                is_limit_down=False, high=price, low=price, up_limit=price * 2, down_limit=price / 2)


def fixture(*, missing_terminal=False, all_cash=False, zero_budget=False):
    days = ["20231229", "20240102", "20240103"]
    quotes = {day: ({} if all_cash else {"A": quote(price)})
              for day, price in zip(days, [10, 12, 15])}
    if missing_terminal:
        quotes[days[-1]] = {}
    cohorts = {days[0]: ["A", "B"]}
    if zero_budget:
        cohorts = {days[0]: ["A"], days[1]: ["B"]}
        quotes[days[1]] = {}
        quotes[days[2]] = {}
    ledger = run_ledger(days, quotes.get, cohorts, fee_bps=10, liquidation_date=days[-1])
    members = pd.DataFrame([dict(symbol=symbol, entry_date=day, formation_date="20231228"
                                if day == days[0] else "20231229")
                            for day, names in cohorts.items() for symbol in names])
    holdings = pd.DataFrame(ledger["holdings"])
    if holdings.empty:
        holdings = pd.DataFrame(columns=HOLDING_COLUMNS)
    boundaries = holdings.loc[holdings.date.isin([days[0], days[-1]])]
    terminal = []
    for h in ledger["holdings"]:
        if h["date"] != days[-1]:
            continue
        missing = h["marked_value"] is None
        terminal.append(dict(lot_id=h["lot_id"], symbol=h["symbol"], cohort=h["cohort"],
                             units=h["units"], terminal_date=days[-1],
                             valuation_class="missing_terminal_quote" if missing else "valued_exit_blocked",
                             reference_value=h["units"] * h["last_observed_price"],
                             last_valid_date=h["last_observed_date"],
                             last_valid_price=h["last_observed_price"],
                             current_marked_value=h["marked_value"]))
    p = dict(portfolio="pb_parent_q1_touch10", metric="pb_parent", quintile=1,
             scenario="touch10", sessions=len(days), last_date=days[-1],
             original_member_months=len(members))
    return [p, members, pd.DataFrame(ledger["orders"]), pd.DataFrame(ledger["daily"]),
            boundaries, pd.DataFrame(terminal, columns=TERMINAL_COLUMNS)]


def test_fees_full_members_and_intended_budget():
    result = attribute_portfolio(*fixture())
    members = result["members"].set_index("symbol")
    assert len(members) == 2
    assert members.loc["A", "intended_slot_budget"] == pytest.approx(500_000)
    assert members.loc["B", "intended_slot_budget"] == pytest.approx(500_000)
    assert members.loc["B", "net_pnl_0"] == 0
    assert members.loc["B", "return_per_intended_budget_strict"] == 0
    buy = 500_000 / 1.001
    sell = buy * 1.5
    expected = sell - buy - (buy + sell) * 0.001
    assert members.loc["A", "net_pnl_0"] == pytest.approx(expected)
    assert result["summary"]["gross_pnl_0_same_path"] == pytest.approx(sell - buy)
    assert result["summary"]["failed_buy_fraction"] == 0.5
    assert result["summary"]["net_pnl_strict"] == pytest.approx(expected)


def test_cross_year_mark_carry_not_sale_year_assignment():
    args = fixture()
    result = attribute_portfolio(*args)
    years = {x["year"]: x for x in result["annual"]}
    buy = 500_000 / 1.001
    assert years[2023]["net_pnl_0"] == pytest.approx(-buy * .001)
    assert years[2024]["net_pnl_0"] == pytest.approx(buy * .5 - buy * 1.5 * .001)
    assert sum(x["net_pnl_0"] for x in years.values()) == pytest.approx(result["summary"]["net_pnl_0"])


def test_unpriced_strict_and_reference_sensitivities():
    result = attribute_portfolio(*fixture(missing_terminal=True))
    row = result["members"].set_index("symbol").loc["A"]
    assert row.net_pnl_0 == pytest.approx(-500_000)
    assert pd.isna(row.net_pnl_strict)
    ref = 500_000 / 1.001 * 1.2
    assert row.net_pnl_50 == pytest.approx(-500_000 + ref / 2)
    assert row.net_pnl_100 == pytest.approx(-500_000 + ref)
    assert result["summary"]["net_pnl_strict"] is None
    assert result["months"].net_pnl_strict.isna().all()
    assert result["annual"][-1]["net_pnl_strict"] is None
    assert result["summary"]["terminal_cash"] == pytest.approx(500_000)


def test_no_reference_not_silently_zeroed():
    args = fixture(missing_terminal=True)
    args[-1].loc[:, "reference_value"] = float("nan")
    result = attribute_portfolio(*args)
    assert result["summary"]["net_pnl_0"] == pytest.approx(-500_000)
    assert result["summary"]["net_pnl_50"] is None
    assert result["summary"]["net_pnl_100"] is None
    assert result["summary"]["unknown_reference_lots"] == 1


def test_all_cash_members_retained():
    result = attribute_portfolio(*fixture(all_cash=True))
    assert len(result["members"]) == 2
    assert result["lots"].empty
    assert result["summary"]["net_pnl_strict"] == 0
    assert result["summary"]["daily_mean_cash_fraction_initial"] == 1
    assert result["summary"]["cash_year_exposure"] == pytest.approx(INITIAL * 5 / 365)
    assert all(x["net_pnl_strict"] == 0 for x in result["annual"])


def test_zero_budget_return_remains_unknown():
    result = attribute_portfolio(*fixture(zero_budget=True))
    row = result["members"].set_index("symbol").loc["B"]
    assert row.intended_slot_budget == pytest.approx(0, abs=1e-10)
    assert row.net_pnl_0 == 0
    assert pd.isna(row.return_per_intended_budget_0)


@pytest.mark.parametrize("corruption,match", [
    ("duplicate_member", "duplicate member"), ("extra_member", "not one-to-one"),
    ("wrong_budget", "budget reconstruction"), ("wrong_formation", "formation not before"),
    ("unfilled_fee", "unfilled economic"), ("unknown_side", "order side"),
])
def test_rejects_broken_contract(corruption, match):
    args = deepcopy(fixture())
    if corruption == "duplicate_member":
        args[1] = pd.concat([args[1], args[1].iloc[[0]]], ignore_index=True)
    elif corruption == "extra_member":
        args[1].loc[1, "symbol"] = "C"
    elif corruption == "wrong_budget":
        args[2].loc[args[2].side.eq("buy"), "budget"] += 1
    elif corruption == "wrong_formation":
        args[1].loc[0, "formation_date"] = "20240101"
    elif corruption == "unfilled_fee":
        args[2].loc[args[2].status.eq("expired"), "fee"] = 1
    else:
        args[2].loc[0, "side"] = "invalid"
    with pytest.raises(ValueError, match=match):
        attribute_portfolio(*args)


def test_cash_leap_year_calendar_and_year_split():
    daily = pd.DataFrame(dict(date=["20231231", "20240102", "20240301"], cash=[365., 730., 0.],
                              strict_nav=[1000., float("nan"), 1000.],
                              zero_unresolved_nav=[1000., 900., 1000.]))
    rows, years = cash_exposure(daily)
    assert rows.iloc[0].cash_year_exposure == 0
    assert years[2023] == pytest.approx(1)
    assert years[2024] == pytest.approx(1 + 2 * 59)  # Includes Feb 29, fixed ACT/365 divisor.
    assert rows.interest_per_1pct_simple.sum() == pytest.approx(1.2)
    assert pd.isna(rows.iloc[1].cash_fraction_strict_nav)


def test_case_direction_ties_dedup_and_no_backfill():
    rows = []
    for metric, right in (("pb_parent", 2), ("pe_deducted_proxy", 3)):
        for symbol, first, second, ref in (("A", 10, 0, 3), ("B", 10, 0, 0), ("C", 0, 20, 0)):
            for q, pnl in ((1, first), (right, second)):
                rows.append(dict(metric=metric, quintile=q, scenario="touch10", symbol=symbol,
                                 net_pnl_0=pnl, unpriced_reference_value=ref))
    candidates, selected = select_cases(pd.DataFrame(rows), [["pb_parent", 1, 2], ["pe_deducted_proxy", 1, 3]])
    assert len(candidates) == 6
    assert [r["symbol"] for r in selected["cases"]] == ["A", "C"]
    assert len(selected["cases"][0]["reasons"]) == 4
    assert selected["slots"][1]["pnl0_difference"] == -20


def test_case_unknown_reference_fails_exhaustive_ranking():
    symbols = pd.DataFrame([dict(metric="pb_parent", quintile=1, scenario="touch10", symbol="A",
                                 net_pnl_0=1., unpriced_reference_value=float("nan"))])
    with pytest.raises(ValueError, match="unknown reference"):
        select_cases(symbols, [["pb_parent", 1, 2]])
