"""Run all four follow-up lines on hash-frozen inputs, without live API access."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import gettempdir

import numpy as np
import pandas as pd

from .analysis import summarize
from .followup_inputs import read_exports, event_records
from .implementation import collateral_levels, fund_comparison
from .inputs import _read_hashed, read_bundle, audit_pair
from .regimes import classify_regimes
from .robustness import index_account, rolling_comparison, summarize_windows, annual_drag_budget


def _metrics(nav: pd.Series) -> dict:
    result = summarize(nav)
    return {
        k: result[k]
        for k in [
            "start",
            "end",
            "observations",
            "cagr",
            "total_return",
            "daily_volatility_252",
            "max_drawdown",
        ]
    }


def _endpoints(calendar: pd.DatetimeIndex, levels: pd.DataFrame) -> pd.DatetimeIndex:
    dates = pd.Series(calendar, index=calendar.to_period("M")).groupby(level=0).max()
    dates = dates[(dates >= levels.index[0]) & (dates <= levels.index[-1])]
    if calendar[-1].to_period("M") == dates.index[-1] and not calendar[-1].is_month_end:
        dates = dates.iloc[:-1]
    return pd.DatetimeIndex(dates.to_numpy())


def _series(frame: pd.DataFrame, date_field: str, field: str) -> pd.Series:
    dates = pd.to_datetime(frame[date_field].astype(str), format="%Y%m%d", errors="raise")
    values = pd.to_numeric(frame[field], errors="raise")
    if dates.isna().any() or dates.duplicated().any() or not np.isfinite(values).all():
        raise ValueError("invalid or duplicate export values")
    return pd.Series(values.to_numpy(), index=dates).sort_index()


def _robustness(levels: pd.DataFrame, endpoints: pd.DatetimeIndex) -> tuple[dict, dict]:
    cases, full = {}, {}
    for policy in ["monthly", "annual"]:
        for weight in [0.1, 0.2, 0.3, 0.4]:
            for horizon in [60, 120]:
                key = f"{policy}_{int(weight * 100)}_{horizon}"
                rows = rolling_comparison(levels, endpoints, weight, policy, horizon)
                cases[key] = {
                    "policy": policy,
                    "commodity_weight": weight,
                    "horizon_months": horizon,
                    **summarize_windows(rows),
                }
                for row in rows:
                    years = (pd.Timestamp(row["end"]) - pd.Timestamp(row["start"])).days / 365.25
                    row["extra_annual_portfolio_drag_budget_bps"] = annual_drag_budget(
                        1 + row["portfolio_total_return"], 1 + row["equity_total_return"], years
                    )
                budgets = [r["extra_annual_portfolio_drag_budget_bps"] for r in rows]
                cases[key]["cost_budget_bps"] = {
                    "median": float(np.median(budgets)) if budgets else None,
                    "minimum": min(budgets, default=None),
                    "positive_count": sum(x > 0 for x in budgets),
                }
                if weight == 0.2 and policy == "monthly":
                    cases[key]["worst_return_difference_windows"] = sorted(
                        rows, key=lambda r: r["portfolio_cagr"] - r["equity_cagr"]
                    )[:5]
                full[key] = rows
    cohorts = []
    for start in endpoints[endpoints.month == 12]:
        if (endpoints[-1].to_period("M") - start.to_period("M")).n < 60:
            continue
        window = levels.loc[start : endpoints[-1]]
        account = index_account(window, 0.2, "monthly", set(endpoints))
        cohorts.append(
            {
                "entry": str(start.date()),
                "equity": _metrics(window.equity),
                "portfolio": _metrics(account["nav"]),
            }
        )
    subperiods = []
    for left, right in [("2006-12", "2012-12"), ("2012-12", "2019-12"), ("2019-12", "2025-12")]:
        a = endpoints[endpoints.to_period("M") == pd.Period(left)][0]
        b = endpoints[endpoints.to_period("M") == pd.Period(right)][0]
        window = levels.loc[a:b]
        subperiods.append(
            {
                "equity": _metrics(window.equity),
                "portfolio": _metrics(index_account(window, 0.2, "monthly", set(endpoints))["nav"]),
            }
        )
    return {
        "cases": cases,
        "annual_entry_cohorts": cohorts,
        "contiguous_subperiods": subperiods,
        "window_start_weights_reset": True,
        "drawdown_frequency": "daily",
    }, full


def _implementation(
    levels: pd.DataFrame, endpoints: pd.DatetimeIndex, exports: dict, calendar: pd.DatetimeIndex
) -> dict:
    gross = index_account(levels, 0.2, "monthly", set(endpoints))
    years = (levels.index[-1] - levels.index[0]).days / 365.25
    stock = float(levels.equity.iloc[-1] / levels.equity.iloc[0])
    costs = []
    for fee in [0, 10, 50, 100]:
        account = index_account(levels, 0.2, "monthly", set(endpoints), fee)
        costs.append(
            {
                "cost_bps_per_two_sided_traded_notional": fee,
                "annualized_two_sided_rebalance_turnover": account["two_sided_turnover"] / years,
                "cost_paid_per_initial_capital": account["cost_paid"],
                "rebalance_count": account["rebalance_count"],
                **_metrics(account["nav"]),
            }
        )
    low, high = 0.0, 1000.0
    if gross["nav"].iloc[-1] <= stock:
        break_even = 0.0
    elif index_account(levels, 0.2, "monthly", set(endpoints), high)["nav"].iloc[-1] > stock:
        break_even = None
    else:
        for _ in range(40):
            mid = (low + high) / 2
            if index_account(levels, 0.2, "monthly", set(endpoints), mid)["nav"].iloc[-1] > stock:
                low = mid
            else:
                high = mid
        break_even = (low + high) / 2
    rates = _series(exports[("shibor", None)], "date", "on")
    cash_anchor = next(d for d in endpoints if d > rates.index[0])
    cash_levels = levels.loc[cash_anchor:]
    cash = []
    for fraction in [0, 0.5, 1.0]:
        adjusted = cash_levels.copy()
        adjusted["commodity"] = collateral_levels(adjusted.commodity, rates, fraction)
        nav = index_account(adjusted, 0.2, "monthly", set(endpoints))["nav"]
        cash.append(
            {
                "shibor_on_fraction": fraction,
                "cash_rate_is_investable": False,
                "stock_reference": _metrics(cash_levels.equity),
                **_metrics(nav),
            }
        )
    products = {}
    for code in ["159980.SZ", "159981.SZ", "159985.SZ"]:
        basic = exports[("fund_basic", code)]
        if len(basic) != 1:
            raise ValueError("one verified fund identity required")
        close = _series(exports[("fund_daily", code)], "trade_date", "close")
        factor = _series(exports[("fund_adj", code)], "trade_date", "adj_factor")
        navframe = exports[("fund_nav", code)]
        unit = _series(navframe, "nav_date", "unit_nav")
        adj = _series(navframe, "nav_date", "adj_nav")
        expected = calendar[
            (calendar >= max(close.index[0], factor.index[0], unit.index[0]))
            & (calendar <= levels.index[-1])
        ]
        absent = {
            name: int(len(expected.difference(s.index)))
            for name, s in [("close", close), ("factor", factor), ("nav", adj)]
        }
        if any(absent.values()):
            products[code] = {"eligible": False, "missing_session_counts": absent}
            continue
        marks = pd.DataFrame(
            {
                "close": close.reindex(expected),
                "adj_factor": factor.reindex(expected),
                "unit_nav": unit.reindex(expected),
                "adj_nav": adj.reindex(expected),
            }
        )
        product = fund_comparison(
            marks, str(basic.name.iloc[0]), str(basic.benchmark.iloc[0]), "NHCI.NH"
        )
        product.update(
            eligible=True,
            dividend_response_rows=len(exports[("fund_div", code)]),
            valuation_dates_not_announcement_signal=True,
        )
        # Actual product market proxy; equity remains a theoretical total-return reference.
        first = next(d for d in endpoints if d >= marks.index[0])
        market = marks.close * marks.adj_factor
        matched = levels.loc[first:].copy()
        matched["commodity"] = market.reindex(matched.index)
        product["equity_80_product_20_index_scenario"] = _metrics(
            index_account(matched, 0.2, "monthly", set(endpoints))["nav"]
        )
        product["matched_stock_reference"] = _metrics(matched.equity)
        year_start = pd.Timestamp("2024-12-31")
        product["calendar_2025_nav_return"] = float(adj.loc["2025-12-31"] / adj.loc[year_start] - 1)
        products[code] = product
    return {
        "extra_annual_total_portfolio_drag_budget_bps": annual_drag_budget(
            float(gross["nav"].iloc[-1]), stock, years
        ),
        "two_sided_rebalance_fee_breakeven_bps": break_even,
        "fee_search_upper_bound_bps": 1000,
        "rebalance_cost_sensitivities": costs,
        "collateral_scenarios": cash,
        "products": products,
        "cash_and_contract_roll_costs_calibrated": False,
        "cta": {
            "eligible": False,
            "reason": "No complete timestamped, survivorship-controlled CTA universe and net values established. No cherry-picked product proxy used.",
        },
    }


def _regime_summary(labels: list[dict], monthly: pd.DataFrame) -> dict:
    changes = monthly.pct_change(fill_method=None).iloc[1:]
    groups = {}
    for label, (_, row) in zip(labels, changes.iterrows()):
        if label["regime"] is None:
            continue
        groups.setdefault(label["regime"], []).append(
            {
                "equity": float(row.equity),
                "commodity": float(row.commodity),
                "mix": float(0.8 * row.equity + 0.2 * row.commodity),
            }
        )
    summary = {
        key: {
            "months": len(rows),
            **{
                asset: {
                    "mean_monthly_return": float(np.mean([r[asset] for r in rows])),
                    "positive_fraction": float(np.mean([r[asset] > 0 for r in rows])),
                }
                for asset in ["equity", "commodity", "mix"]
            },
        }
        for key, rows in groups.items()
    }
    return {
        "groups": summary,
        "eligible_months": sum(len(v) for v in groups.values()),
        "unavailable_months": len(changes) - sum(len(v) for v in groups.values()),
        "point_in_time_verified_months": sum(x["point_in_time_verified"] for x in labels),
        "conditional_observations_not_spliced_into_wealth": True,
    }


def _macro(
    levels: pd.DataFrame, endpoints: pd.DatetimeIndex, exports: dict, context: pd.DataFrame
) -> tuple[dict, list]:
    monthly = levels.reindex(endpoints)
    events = event_records(exports[("eco_cal", None)])
    labels = classify_regimes(endpoints[:-1], events, require_verified=False)
    result = {
        "release_event_reconstruction": _regime_summary(labels, monthly),
        "historical_vintage_verified": False,
        "prediction_or_timing_effectiveness_established": False,
    }
    strict = classify_regimes(endpoints[:-1], events, require_verified=True)
    result["strict_historical_admission"] = _regime_summary(strict, monthly)
    for lag in [1, 2]:
        records = []
        for api, field, name in [("cn_pmi", "pmi010000", "pmi"), ("cn_ppi", "ppi_yoy", "ppi")]:
            for row in exports[(api, None)].to_dict("records"):
                period = pd.Period(str(row["month"]), freq="M")
                available = (period + lag).start_time
                records.append(
                    {
                        "series": name,
                        "available_at": available.isoformat(),
                        "value": float(row[field]),
                        "vintage_verified": False,
                    }
                )
        lag_labels = classify_regimes(endpoints[:-1], pd.DataFrame(records), False)
        result[f"revised_snapshot_lag_{lag}_months"] = _regime_summary(lag_labels, monthly)
    selected = context.loc[context.series_id.isin(["activity.pmi_manufacturing", "prices.ppi_yoy"])]
    result["existing_observed_archive"] = {
        "rows": len(selected),
        "series": sorted(selected.series_id.unique().tolist()),
        "earliest_available_at": str(selected.available_at.min()) if len(selected) else None,
        "archive_precedes_2025_sample_end": bool(
            len(selected)
            and pd.Timestamp(selected.available_at.min()) < pd.Timestamp("2026-01-01", tz="UTC")
        ),
    }
    return result, labels


def run_followup(manifest_path: Path, output: Path) -> dict:
    output = output.resolve()
    if any(
        (p / ".git").exists()
        for p in [output, *output.parents]
        if p not in {Path.home(), Path(gettempdir())}
    ):
        raise ValueError("outputs must remain outside source repositories")
    if output.exists():
        raise FileExistsError("select a new output directory")
    manifest = json.loads(manifest_path.read_text())
    base_path = Path(manifest["baseline_manifest_path"])
    _read_hashed(base_path, manifest["baseline_manifest_sha256"])
    series, calendars, _ = read_bundle(base_path)
    audit, levels = audit_pair(
        series["H00300.CSI"],
        series["NHCI.NH"],
        calendars["SSE"],
        calendars["SHFE"],
        pd.Timestamp("2006-12-29"),
        pd.Timestamp("2025-12-31"),
    )
    if not audit["eligible"]:
        raise ValueError("frozen baseline calendar audit failed")
    common = calendars["SSE"].intersection(calendars["SHFE"])
    endpoints = _endpoints(common, levels)
    exports, receipts = read_exports(manifest["exports"])
    context_path = Path(manifest["context_snapshot_path"])
    _read_hashed(context_path, manifest["context_snapshot_sha256"])
    context = pd.read_parquet(context_path)
    robustness, windows = _robustness(levels, endpoints)
    implementation = _implementation(levels, endpoints, exports, common)
    macro, labels = _macro(levels, endpoints, exports, context)
    result = {
        "schema_version": 1,
        "study_id": "china_commodity_equity",
        "phase": "four_line_exploration",
        "source_revision": manifest["source_revision"],
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "code_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in [
                "followup_run.py",
                "followup_inputs.py",
                "robustness.py",
                "implementation.py",
                "regimes.py",
            ]
        },
        "series": {
            "equity": {"id": "H00300.CSI", "return_basis": "total_return", "currency": "CNY"},
            "commodity": {
                "id": "NHCI.NH",
                "return_basis": "published_futures_index",
                "currency": "CNY",
            },
        },
        "baseline": audit,
        "robustness": robustness,
        "implementation": implementation,
        "macro": macro,
        "source_audit": {
            "requests": len(receipts),
            "empty_or_nonzero_responses": [
                {"id": r["id"], "api": r["api"], "rows": r["rows"], "code": r["code"]}
                for r in receipts
                if not r.get("rows") or r.get("code") != 0
            ],
        },
        "limitations": [
            "Overlapping windows are descriptive, not future probabilities.",
            "Idealized index sleeves omit contract quantities, margin calls and actual slippage.",
            "Shibor is a rate proxy, not an achievable collateral investment.",
            "ETF NAV/adjustment factors are revised provider proxies, not executable NAV quotes.",
            "Economic-event publication dates do not authenticate historical vintages; no macro timing claim.",
        ],
    }
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    private = (
        json.dumps(
            {"windows": windows, "macro_decisions": labels, "receipts": receipts},
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    output.mkdir(parents=True, exist_ok=False)
    (output / "reviewed-candidate.json").write_text(text)
    (output / "full-diagnostics.json").write_text(private)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_followup(args.manifest, args.output)
    print(
        json.dumps(
            {
                "window_cases": len(result["robustness"]["cases"]),
                "macro_eligible": result["macro"]["release_event_reconstruction"][
                    "eligible_months"
                ],
                "strict_macro_eligible": result["macro"]["strict_historical_admission"][
                    "eligible_months"
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
