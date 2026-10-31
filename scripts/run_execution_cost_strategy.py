import argparse
import inspect
import importlib.metadata
import hashlib
import json
from pathlib import Path
import pandas as pd
from quant_platform.backtest.legacy.execution_sim import (
    ExecutionSimConfig,
    TradeFeeModel,
    simulate_execution_adjusted_nav,
    prepare_execution_tables,
)
from market_research.studies.ashare_execution_costs.strategy import (
    accounting_overlay,
    anchor_exceedance,
    turnover_stress,
    expanded_scenarios,
)

parser = argparse.ArgumentParser(description="Diagnostic existing-strategy cost sensitivity")
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--pilot", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--expanded-public", type=Path)
args = parser.parse_args()
src, pilot, out = args.source, args.pilot, args.output
if out.exists() and any(out.iterdir()):
    raise FileExistsError("output directory must be new or empty")
out.mkdir(parents=True, exist_ok=True)
reference = json.loads((args.expanded_public or pilot).read_text())
anchors = reference["pooled"]["cost_surface"]
expanded = expanded_scenarios(reference) if args.expanded_public else None
frames = [
    pd.read_parquet(src / f"{n}.parquet")
    for n in ("daily_ledger", "fills", "orders", "performance")
]
source_days = frames[0].trade_date.astype(str)
if source_days.min() < "20230828" or source_days.max() > "20250331":
    raise ValueError("This runner uses the audited post-2023-08-28 Q1 2025 fee sensitivity period")
request = json.loads((src / ".runtime/microcap-request.json").read_text())


def artifact(key):
    return src / ".runtime/artifacts/sha256" / request["inputs"][key].split("/")[-1]


for key, ref in request["inputs"].items():
    if hashlib.sha256(artifact(key).read_bytes()).hexdigest() != ref.split("/")[-1]:
        raise ValueError("runtime content-addressed input hash mismatch")
positions = pd.read_parquet(artifact("positions_ref"))
pricing = pd.read_parquet(artifact("pricing_ref"))
base_cfg = dict(request["execution"]["ledger_config"])
base_cfg["liquidity_cols"] = tuple(base_cfg["liquidity_cols"])
prepared = prepare_execution_tables(
    pricing,
    ExecutionSimConfig(**base_cfg),
    price_col="adj_close",
    tradable_col="tradable",
    limit_up_col="limit_up",
    limit_down_col="limit_down",
)
rows = []
stress = []
reruns = []
for capital in (10_000_000, 100_000_000, 1_000_000_000):
    for size in () if expanded else (10_000, 100_000, 1_000_000, 10_000_000):
        a = {r["side"]: r for r in anchors if r["reference_notional_cny"] == size}
        buy = a["buy"]["full_order_cost_bp"]["p50"]
        sell = a["sell"]["full_order_cost_bp"]["p50"]
        daily, s = accounting_overlay(
            *frames,
            initial_capital=1_000_000,
            capital=capital,
            buy_fee_bp=1.0,
            sell_fee_bp=6.0,
            buy_static_bp=buy,
            sell_static_bp=sell,
        )
        s.update(
            anchor_notional_cny=size,
            buy_static_bp=buy,
            sell_static_bp=sell,
            buy_pilot_full_coverage_rate=a["buy"]["full_coverage_rate"],
            sell_pilot_full_coverage_rate=a["sell"]["full_coverage_rate"],
        )
        s.update(anchor_exceedance(frames[2], scale=capital / 1_000_000, reference_notional=size))
        rows.append(s)
        daily.to_csv(out / f"overlay-{capital}-{size}.csv", index=False)
        t = turnover_stress(
            capital, sessions=250, one_way_turnover=0.6, buy_bp=buy + 1.0, sell_bp=sell + 6.0
        )
        t["anchor_notional_cny"] = size
        stress.append(t)
    # actual modeled execution: gross, assumed fees, borrowed10k and1m anchors
    scenarios = expanded or [
        {"scenario": "gross", "anchor_notional_cny": 0},
        {"scenario": "fee_only", "anchor_notional_cny": 0},
        {"scenario": "fee_static_10k", "anchor_notional_cny": 10_000},
        {"scenario": "fee_static_1m", "anchor_notional_cny": 1_000_000},
    ]
    for scenario in scenarios:
        variant, size = scenario["scenario"], scenario["anchor_notional_cny"]
        cfg = dict(request["execution"]["ledger_config"])
        cfg["portfolio_value"] = capital
        cfg["liquidity_cols"] = tuple(cfg["liquidity_cols"])
        a = {r["side"]: r for r in anchors if r["reference_notional_cny"] == size}
        fee = (
            None
            if variant == "gross"
            else TradeFeeModel(
                buy_commission_bps=1.0,
                sell_commission_bps=1.0,
                sell_stamp_duty_bps=5.0,
                transfer_fee_bps=0.0,
                min_commission=0.0,
                buy_slippage_bps=a["buy"]["full_order_cost_bp"]["p50"] if size else 0.0,
                sell_slippage_bps=a["sell"]["full_order_cost_bp"]["p50"] if size else 0.0,
                portfolio_value=capital,
            )
        )
        result = simulate_execution_adjusted_nav(
            positions,
            pricing,
            ExecutionSimConfig(**cfg),
            price_col="adj_close",
            tradable_col="tradable",
            limit_up_col="limit_up",
            limit_down_col="limit_down",
            transaction_cost_bps=0.0,
            prepared_tables=prepared,
            trade_fee_model=fee,
            price_basis="daily_clean.adjusted_close_proxy",
        )
        print(capital, variant, "simulation completed", flush=True)
        perf = result.daily
        ledger = perf[["trade_date", "cash", "invested_value", "portfolio_value"]].rename(
            columns={
                "period_end": "trade_date",
                "invested_value": "positions_value",
                "portfolio_value": "nav",
            }
        )
        fills = result.fills
        orders = result.orders
        assert len(ledger) == len(frames[0])
        assert ((ledger.nav - ledger.cash - ledger.positions_value).abs() < 1e-4).all()
        assert abs(fills.transaction_cost.sum() - perf.transaction_cost.sum()) < 1e-4
        assert abs(orders.filled_notional.sum() - fills.filled_notional.sum()) < 1e-3
        ledger.to_csv(out / f"modeled-ledger-{capital}-{variant}.csv", index=False)
        # aggregate only, no symbols/order IDs
        row = {
            "capital_cny": capital,
            "scenario": variant,
            "anchor_notional_cny": size,
            "terminal_nav": float(ledger.nav.iloc[-1] / capital),
            "transaction_cost_cny": float(fills.transaction_cost.sum()),
            "negative_cash_sessions": int((ledger.cash < -1e-6).sum()),
        }
        for side in ("buy", "sell"):
            row[f"executed_{side}_cny"] = float(
                fills.loc[fills.side.eq(side)].filled_notional.sum()
            )
            row[f"unfilled_{side}_cny"] = float(
                orders.loc[orders.side.eq(side)].unfilled_notional.sum()
            )
        previous_value = perf.portfolio_value.shift(1, fill_value=capital)
        row["mean_one_way_turnover"] = float((perf.traded_notional / previous_value / 2).mean())
        row["max_one_way_turnover"] = float((perf.traded_notional / previous_value / 2).max())
        row["partially_filled_orders"] = int(
            ((orders.filled_notional > 0) & (orders.unfilled_notional > 1e-6)).sum()
        )
        row["zero_fill_orders"] = int((orders.filled_notional <= 1e-6).sum())
        if expanded:
            row.update(
                {k: v for k, v in scenario.items() if k not in ("scenario", "anchor_notional_cny")}
            )
        reruns.append(row)
        pd.DataFrame(reruns).to_csv(out / "modeled-summary.csv", index=False)
if not expanded:
    pd.DataFrame(rows).to_csv(out / "overlay-summary.csv", index=False)
    pd.DataFrame(stress).to_csv(out / "turnover-stress.csv", index=False)
pd.DataFrame(reruns).to_csv(out / "modeled-summary.csv", index=False)
receipt = {
    "evidence": "diagnostic_shared_simulator_and_frozen_path_sensitivity",
    "source_period": [source_days.min(), source_days.max()],
    "runtime_input_refs": request["inputs"],
    "simulator_configuration": base_cfg,
    "original_simulator_cost_bp_replaced": 5.0,
    "modeled_rerun_transaction_cost_bp": 0.0,
    "static_reference_dates": sorted(reference.get("by_day", {})),
    "static_reference_sha256": hashlib.sha256(
        (args.expanded_public or pilot).read_bytes()
    ).hexdigest(),
    "expanded_reference": bool(expanded),
    "conditional_static_anchors": expanded,
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "engine_modules_sha256": {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in Path(inspect.getfile(simulate_execution_adjusted_nav)).parent.glob("*.py")
    },
    "fee_model_module_sha256": hashlib.sha256(
        Path(inspect.getfile(TradeFeeModel)).read_bytes()
    ).hexdigest(),
    "engine_module_sha256": hashlib.sha256(
        Path(inspect.getfile(simulate_execution_adjusted_nav)).read_bytes()
    ).hexdigest(),
    "simulator_distribution_version": importlib.metadata.version("quant-platform"),
    "runtime_request_sha256": hashlib.sha256(
        (src / ".runtime/microcap-request.json").read_bytes()
    ).hexdigest(),
    "runtime_input_sha256": {
        key: hashlib.sha256(artifact(key).read_bytes()).hexdigest() for key in request["inputs"]
    },
    "output_sha256": {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob("*.csv")
    },
    "source_sha256": {
        n: hashlib.sha256((src / f"{n}.parquet").read_bytes()).hexdigest()
        for n in ("daily_ledger", "fills", "orders", "performance", "positions")
    },
    "pilot_sha256": hashlib.sha256(pilot.read_bytes()).hexdigest(),
    "fee_assumptions": {
        "inclusive_commission_bp_each_side": 1.0,
        "minimum_commission_cny": 0,
        "separate_transfer_bp": 0.0,
        "seller_stamp_bp": 5,
        "seller_stamp_effective_from": "2023-08-28",
        "tax_source": "https://shanghai.chinatax.gov.cn/zcfw/zcfgk/yhs/202308/t468451.html",
    },
    "limitations": [
        "Original diagnostic input release times, corporate actions and delisting settlement unverified.",
        "Static reference medians condition on complete ten-level coverage and are borrowed across stocks and dates; not an ex ante Q1 2025 prediction.",
        "No impact, resilience, queue, intraday path or net-alpha inference.",
        "Capital overlays freeze fills; modeled reruns use shared5% daily amount participation proxy.",
        "Zero minimum commission and inclusive flat commission are sensitivity assumptions; source includes Beijing and venue-specific fee handling is absent.",
        "Orders do not expose limit/suspension attribution; constraints configured, no invented reason attribution.",
    ],
}
(out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(pd.DataFrame(reruns).to_string(index=False))
