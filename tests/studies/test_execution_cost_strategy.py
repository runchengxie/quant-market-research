import importlib

import pandas as pd
import pytest


def module():
    spec = importlib.util.find_spec("market_research.studies.ashare_execution_costs.strategy")
    assert spec is not None, "strategy accounting companion is missing"
    return importlib.import_module(spec.name)


def inputs():
    ledger = pd.DataFrame(
        {
            "trade_date": ["20250103", "20250106"],
            "cash": [49.95, 49.90],
            "positions_value": [50.0, 55.0],
            "nav": [99.95, 104.90],
        }
    )
    fills = pd.DataFrame(
        {
            "trade_date": ["20250103", "20250106"],
            "side": ["buy", "sell"],
            "filled_notional": [100.0, 100.0],
            "transaction_cost": [0.05, 0.05],
        }
    )
    orders = pd.DataFrame(
        {
            "side": ["buy", "sell"],
            "requested_notional": [150.0, 100.0],
            "filled_notional": [100.0, 100.0],
            "unfilled_notional": [50.0, 0.0],
        }
    )
    perf = pd.DataFrame(
        {
            "period_end": ["20250103", "20250106"],
            "transaction_cost": [0.05, 0.05],
            "traded_notional": [100.0, 100.0],
        }
    )
    return ledger, fills, orders, perf


def test_reconciled_overlay_replaces_original_cost_and_only_charges_fills():
    daily, summary = module().accounting_overlay(
        *inputs(),
        initial_capital=100.0,
        capital=1000.0,
        buy_fee_bp=1.0,
        sell_fee_bp=6.0,
        buy_static_bp=2.0,
        sell_static_bp=3.0,
    )
    assert daily.gross_nav.tolist() == pytest.approx([1.0, 1.05])
    assert daily.fee_only_nav.iloc[-1] == pytest.approx(1.0493)
    assert daily.fee_static_nav.iloc[-1] == pytest.approx(1.0488)
    assert summary["unfilled_buy_cny"] == 500.0
    assert summary["executed_sell_cny"] == 1000.0
    assert summary["original_cost_cny"] == 1.0
    assert "symbol" not in daily.columns


def test_daily_returns_compound_back_to_nav():
    daily, _ = module().accounting_overlay(*inputs(), initial_capital=100.0, capital=100.0)
    assert (1 + daily.fee_static_return).prod() == pytest.approx(daily.fee_static_nav.iloc[-1])


@pytest.mark.parametrize("damage", ["nav", "cost", "order", "side", "duplicate", "nan"])
def test_rejects_unreconciled_and_invalid_inputs(damage):
    ledger, fills, orders, perf = inputs()
    if damage == "nav":
        ledger.loc[0, "nav"] += 1
    if damage == "cost":
        perf.loc[0, "transaction_cost"] += 1
    if damage == "order":
        orders.loc[0, "unfilled_notional"] += 1
    if damage == "side":
        fills.loc[0, "side"] = "short"
    if damage == "duplicate":
        ledger.loc[1, "trade_date"] = ledger.loc[0, "trade_date"]
    if damage == "nan":
        fills.loc[0, "filled_notional"] = float("nan")
    with pytest.raises(ValueError):
        module().accounting_overlay(
            ledger, fills, orders, perf, initial_capital=100.0, capital=100.0
        )


def test_stress_one_way_is_buy_plus_sell_and_compounded():
    row = module().turnover_stress(
        10_000_000, sessions=2, one_way_turnover=0.6, buy_bp=10.0, sell_bp=20.0
    )
    assert row["daily_cost_fraction"] == pytest.approx(0.0018)
    assert row["terminal_cost_only_nav"] == pytest.approx((1 - 0.0018) ** 2)
    assert row["daily_initial_capital_cost_cny"] == 18000.0


def test_rejects_nonpositive_capital_and_negative_cost():
    with pytest.raises(ValueError):
        module().accounting_overlay(*inputs(), initial_capital=100.0, capital=0.0)
    with pytest.raises(ValueError):
        module().accounting_overlay(
            *inputs(), initial_capital=100.0, capital=100.0, buy_static_bp=-1
        )


def test_requested_notional_anchor_comparison_does_not_impute_missing_depth():
    result = module().anchor_exceedance(inputs()[2], scale=10.0, reference_notional=1200.0)
    assert result["buy_requested_notional_above_anchor_fraction"] == 1.0
    assert result["sell_requested_notional_above_anchor_fraction"] == 0.0
    assert result["interpretation"] == "size_comparison_only_not_matched_book_coverage"


def test_unfunded_overlay_exposes_shortfall_and_preserves_holdings():
    daily, summary = module().accounting_overlay(
        *inputs(), initial_capital=100.0, capital=100.0, buy_static_bp=6000.0, sell_static_bp=0.0
    )
    assert daily.positions_cny.tolist() == [50.0, 55.0]
    assert daily.fee_static_cash_cny.iloc[0] == pytest.approx(-10.0)
    assert summary["fee_static_negative_cash_sessions"] == 2
    assert summary["fee_static_max_funding_shortfall_cny"] == pytest.approx(10.0)


@pytest.mark.parametrize("sessions,buy_bp", [(0, 1.0), (2, -1.0), (2, 20000.0)])
def test_invalid_stress_inputs(sessions, buy_bp):
    with pytest.raises(ValueError):
        module().turnover_stress(
            100.0, sessions=sessions, one_way_turnover=0.6, buy_bp=buy_bp, sell_bp=0.0
        )


def expanded_reference():
    return {
        "schema_version": "ashare_execution_costs.expansion.public.v1",
        "permission": {"status": "confirmed_by_owner"},
        "review": {"source_summary_sha256": "a" * 64},
        "pooled": {
            "cost_surface": [
                {
                    "side": side,
                    "reference_notional_cny": size,
                    "full_order_cost_bp": {"p50": bp},
                    "full_coverage_rate": coverage,
                }
                for side, size, bp, coverage in [
                    ("buy", 100000, 9.0, 0.99),
                    ("sell", 100000, 8.0, 0.98),
                    ("buy", 1000000, 21.0, 0.6),
                    ("sell", 1000000, 20.0, 0.7),
                ]
            ]
        },
    }


def test_expanded_reference_retains_conditional_medians_and_coverage():
    rows = module().expanded_scenarios(expanded_reference())
    assert [(r["scenario"], r["anchor_notional_cny"]) for r in rows] == [
        ("fee_expanded_100k", 100000),
        ("fee_expanded_1m", 1000000),
    ]
    assert rows[1]["buy_static_bp"] == 21.0
    assert rows[1]["sell_static_bp"] == 20.0
    assert rows[1]["buy_reference_full_coverage_rate"] == 0.6


@pytest.mark.parametrize(
    "damage", ["unreviewed", "permission", "missing", "duplicate", "nan", "coverage"]
)
def test_expanded_reference_rejects_unreviewed_or_invalid_anchor(damage):
    reference = expanded_reference()
    if damage == "unreviewed":
        reference["review"] = {}
    elif damage == "permission":
        reference["permission"]["status"] = "unknown"
    elif damage == "missing":
        reference["pooled"]["cost_surface"].pop()
    elif damage == "duplicate":
        reference["pooled"]["cost_surface"].append(reference["pooled"]["cost_surface"][0])
    elif damage == "nan":
        reference["pooled"]["cost_surface"][0]["full_order_cost_bp"]["p50"] = float("nan")
    else:
        reference["pooled"]["cost_surface"][0]["full_coverage_rate"] = 1.1
    with pytest.raises(ValueError):
        module().expanded_scenarios(reference)
