import importlib.util
from pathlib import Path

import pytest


path = Path(__file__).resolve().parents[1] / "scripts" / "analyze_grouped_valuation_unresolved.py"
spec = importlib.util.spec_from_file_location("unresolved_analysis", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
analyze = module.terminal_analysis


def holding(lot, source, price=None, last_price=10.0, last_date="20260102", units=2.0):
    return dict(
        date="20260106",
        lot_id=lot,
        symbol=lot,
        cohort="20260102",
        units=units,
        requested_date="20260105",
        mark_source=source,
        mark_price=price,
        marked_value=units * price if price is not None else None,
        last_observed_price=last_price,
        last_observed_date=last_date,
    )


def portfolio(holdings, cash=40.0):
    current = sum(h["marked_value"] or 0 for h in holdings)
    missing = sum(h["mark_price"] is None for h in holdings)
    return dict(
        portfolio="pb_parent_q1_touch10",
        metric="pb_parent",
        quintile=1,
        scenario="touch10",
        last_date="20260106",
        final=dict(
            date="20260106",
            cash=cash,
            known_marked_value=current,
            holding_lots=len(holdings),
            unresolved_lots=missing,
            pending_exit_lots=len(holdings),
            zero_unresolved_nav=cash + current,
            strict_nav=None if missing else cash + current,
        ),
    )


def run(holdings, anchors, attempts=None):
    return analyze(
        portfolio(holdings),
        holdings,
        anchors,
        attempts or {},
        ["20260102", "20260105", "20260106"],
        initial_capital=100.0,
    )


def test_two_scopes_preserve_current_value_cash_and_units():
    h = [
        holding("missing", "unresolved_missing_quote"),
        holding("terminal", "unresolved_terminal", last_price=5.0),
        holding(
            "blocked", "observed_adjusted_close", price=15.0, last_price=15.0, last_date="20260106"
        ),
    ]
    anchors = {
        "missing": {"price": 10.0, "date": "20260102"},
        "terminal": {"price": 5.0, "date": "20260102"},
        "blocked": {"price": 15.0, "date": "20260106"},
    }
    attempts = {"blocked": {"date": "20260106", "status": "pending", "reason": "lower_limit"}}
    result = run(h, anchors, attempts)
    rows = result["sensitivities"]
    assert [r["scenario_value"] for r in rows[:3]] == [70.0, 85.0, 100.0]
    assert [r["scenario_value"] for r in rows[3:]] == [40.0, 70.0, 100.0]
    assert all(r["cash"] == 40.0 and not r["units_changed"] for r in rows)
    assert [r["units"] for r in result["lots"]] == [2.0, 2.0, 2.0]
    assert result["summary"]["class_counts"] == {
        "terminal_unsettled": 1,
        "missing_terminal_quote": 1,
        "valued_exit_blocked": 1,
    }
    assert result["lots"][0]["reference_weight_initial"] == 0.2
    assert result["lots"][0]["reference_weight_total"] == 0.2
    assert result["lots"][2]["last_exit_reason"] == "lower_limit"


def test_age_uses_persisted_sessions_not_weekdays_or_elapsed_days():
    result = run([holding("A", "unresolved_terminal")], {"A": {"price": 10.0, "date": "20260102"}})
    row = result["lots"][0]
    assert row["last_quote_age_sessions"] == 2
    assert row["last_quote_age_calendar_days"] == 4


def test_unknown_reference_is_visible_and_nonzero_scenarios_stay_unknown():
    h = holding("A", "unresolved_missing_quote", last_price=None, last_date=None)
    result = run([h], {})
    assert result["summary"]["unknown_reference_lots"] == 1
    assert not result["summary"]["reference_complete"]
    assert result["summary"]["reference_total_value"] is None
    assert result["lots"][0]["reference_weight_total"] is None
    assert result["lots"][0]["last_quote_age_sessions"] is None
    assert [r["scenario_value"] for r in result["sensitivities"]] == [
        40.0,
        None,
        None,
        40.0,
        None,
        None,
    ]
    assert all(r["unknown_reference_lots"] == 1 for r in result["sensitivities"])
    assert all(not r["reference_complete"] for r in result["sensitivities"])


def test_valued_but_unexited_is_not_called_liquidated():
    h = holding("A", "observed_adjusted_close", price=10.0, last_price=10.0, last_date="20260106")
    result = run([h], {"A": {"price": 10.0, "date": "20260106"}})
    assert result["summary"]["strict_terminal_value_available"]
    assert not result["summary"]["fully_liquidated"]
    assert result["summary"]["valued_but_unexited_lots"] == 1


def test_empty_inventory_is_cash_only_for_both_scopes():
    result = run([], {})
    assert result["summary"]["fully_liquidated"]
    assert all(r["scenario_value"] == 40.0 for r in result["sensitivities"])


@pytest.mark.parametrize(
    "anchor",
    [
        {"price": 10.0, "date": "20260107"},
        {"price": 10.0, "date": "20260104"},
        {"price": 11.0, "date": "20260102"},
    ],
)
def test_future_off_calendar_and_retained_anchor_mismatch_fail(anchor):
    with pytest.raises(ValueError):
        run([holding("A", "unresolved_terminal")], {"A": anchor})


def test_filled_final_sell_cannot_coexist_with_held_lot():
    with pytest.raises(ValueError):
        run(
            [holding("A", "unresolved_terminal")],
            {"A": {"price": 10.0, "date": "20260102"}},
            {"A": {"date": "20260106", "status": "filled", "reason": None}},
        )


def test_current_quote_cannot_be_invented_for_terminal_asset():
    h = holding("A", "unresolved_terminal", price=10.0)
    with pytest.raises(ValueError):
        run([h], {"A": {"price": 10.0, "date": "20260102"}})
