"""Fourth-round product and sample sensitivity diagnostics on frozen inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import gettempdir

import numpy as np
import pandas as pd

from .followup_inputs import read_exports
from .followup_run import _endpoints, _metrics, _series
from .funded_products import funded_products
from .implementation import collateral_levels
from .inputs import _read_hashed, read_bundle, audit_pair
from .risk_controls import lagged_risk_control
from .robustness import index_account


def cash_curve(index: pd.DatetimeIndex, rates: pd.Series, fraction: float) -> pd.Series:
    return collateral_levels(pd.Series(1.0, index=index), rates, fraction)


def rule_cash_account(stock: pd.Series, cash: pd.Series, decisions: pd.Series) -> pd.Series:
    dates = stock.loc[decisions.index[0] :].index
    weights = decisions.reindex(dates).ffill()
    holdings = np.array([weights.iloc[0], 1 - weights.iloc[0]])
    nav = pd.Series(1.0, index=dates)
    for i in range(1, len(dates)):
        holdings *= [
            stock.loc[dates[i]] / stock.loc[dates[i - 1]],
            cash.loc[dates[i]] / cash.loc[dates[i - 1]],
        ]
        nav.iloc[i] = holdings.sum()
        if dates[i] in decisions.index:
            holdings = nav.iloc[i] * np.array([weights.iloc[i], 1 - weights.iloc[i]])
    return nav


def sensitivities(levels: pd.DataFrame, endpoints: pd.DatetimeIndex, rates: pd.Series) -> dict:
    rules = {n: lagged_risk_control(levels, endpoints, n) for n in [252, 504, 756]}
    common_start = max(x["nav"].index[0] for x in rules.values())
    rows = []
    for start in ["2006-12-29", "2007-12-28", "2009-12-31", "2012-12-31", "2019-12-31"]:
        window = levels.loc[start:]
        a = index_account(window, 0.2, "monthly", set(endpoints))["nav"]
        cash = window.assign(commodity=1.0)
        rows.append(
            {
                "requested_start": start,
                "equity": _metrics(window.equity),
                "commodity_20": _metrics(a),
                "cash_20": _metrics(index_account(cash, 0.2, "monthly", set(endpoints))["nav"]),
            }
        )
    matching = []
    for lookback, rule in rules.items():
        for common in [False, True]:
            start = common_start if common else rule["nav"].index[0]
            window = levels.loc[start:]
            decisions = rule["decision_weights"].loc[start:]
            for fraction in [0, 0.5]:
                cash = cash_curve(window.index, rates, fraction)
                stock_cash = rule_cash_account(window.equity, cash, decisions)
                fixed_cash = window.assign(commodity=cash)
                matching.append(
                    {
                        "lookback_sessions": lookback,
                        "common_start_across_lookbacks": common,
                        "cash_shibor_fraction": fraction,
                        "equity": _metrics(window.equity),
                        "commodity_20": _metrics(
                            index_account(window, 0.2, "monthly", set(endpoints))["nav"]
                        ),
                        "cash_20": _metrics(
                            index_account(fixed_cash, 0.2, "monthly", set(endpoints))["nav"]
                        ),
                        "risk_cash": _metrics(stock_cash),
                    }
                )
    # Predeclared calendar-year stress, only rules with a valid prior decision are admitted.
    stress = []
    for n, rule in rules.items():
        if rule["nav"].index[0] <= pd.Timestamp("2007-12-28"):
            sub = rule["nav"].loc["2007-12-28":"2008-12-31"]
            stress.append({"lookback_sessions": n, "eligible": True, "metrics": _metrics(sub)})
        else:
            stress.append(
                {
                    "lookback_sessions": n,
                    "eligible": False,
                    "first_estimated_month_end": str(rule["nav"].index[0].date()),
                    "reason": "insufficient pre-2008 estimation history",
                }
            )
    return {
        "fixed_starts": rows,
        "risk_grid": matching,
        "stress_2008_rule_admission": stress,
        "lookbacks_prespecified_for_this_round": [252, 504, 756],
        "cash_rate_is_investable": False,
        "training_start": str(levels.index[0].date()),
    }


def product_cases(levels, calendar, endpoints, rates, exports):
    marks = {}
    for code in ["510300.SH", "159980.SZ", "159981.SZ", "159985.SZ"]:
        basic = exports[("fund_basic", code)]
        if len(basic) != 1:
            raise ValueError("fund identity missing")
        close = _series(exports[("fund_daily", code)], "trade_date", "close")
        factor = _series(exports[("fund_adj", code)], "trade_date", "adj_factor")
        nav = _series(exports[("fund_nav", code)], "nav_date", "adj_nav")
        unit = _series(exports[("fund_nav", code)], "nav_date", "unit_nav")
        marks[code] = {
            "close": close,
            "market": close * factor,
            "nav": nav,
            "unit": unit,
            "benchmark": str(basic.benchmark.iloc[0]),
        }
    start = next(d for d in endpoints if d >= max(x["market"].index.min() for x in marks.values()))
    expected = calendar[(calendar >= start) & (calendar <= levels.index[-1])]
    for code, mark in marks.items():
        for name in ["close", "market", "nav", "unit"]:
            if len(expected.difference(mark[name].dropna().index)):
                raise ValueError("missing own-calendar product or NAV observation")
    products, private = {}, {}
    for code in ["159980.SZ", "159981.SZ", "159985.SZ"]:
        rows = []
        stock = marks["510300.SH"]
        product = marks[code]
        for fraction in [0, 0.5]:
            cash = cash_curve(expected, rates, fraction)
            for fee in [0, 10, 50]:
                for basis in ["market", "nav"]:
                    panel = pd.DataFrame(
                        {
                            "stock": stock[basis].reindex(expected),
                            "product": product[basis].reindex(expected),
                            "cash": cash,
                        }
                    )
                    for strategy, weights in [
                        ("equity", [1.0, 0.0, 0.0]),
                        ("product_20", [0.8, 0.2, 0.0]),
                        ("cash_20", [0.8, 0.0, 0.2]),
                    ]:
                        account = funded_products(panel, weights, set(endpoints), fee)
                        nav = account.pop("nav")
                        ledger = account.pop("ledger")
                        identity = f"{code}_{fraction}_{fee}_{basis}_{strategy}"
                        private[identity] = ledger
                        rows.append(
                            {
                                "strategy": strategy,
                                "basis": basis,
                                "fee_bps_per_side": fee,
                                "cash_shibor_fraction": fraction,
                                **_metrics(nav),
                                **account,
                            }
                        )
        premium = product["close"].reindex(expected) / product["unit"].reindex(expected) - 1
        products[code] = {
            "issuer_benchmark": product["benchmark"],
            "matches_NHCI": False,
            "premium_min": float(premium.min()),
            "premium_max": float(premium.max()),
            "premium_start": float(premium.iloc[0]),
            "premium_end": float(premium.iloc[-1]),
            "cases": rows,
        }
    return {
        "stock_product": "510300.SH",
        "start": str(start.date()),
        "end": str(expected[-1].date()),
        "observations": len(expected),
        "products": products,
        "fractional_adjusted_price_proxy": True,
        "actual_share_lots_and_dividend_cashflows_reconstructed": False,
        "investor_costs_are_assumptions": True,
        "manager_fees_subtracted_again": False,
        "nav_is_retrospective_not_signal": True,
    }, private


def run_forward(manifest_path: Path, output: Path) -> dict:
    output = output.resolve()
    if output.exists():
        raise FileExistsError("new output directory required")
    if any(
        (p / ".git").exists()
        for p in [output, *output.parents]
        if p not in {Path.home(), Path(gettempdir())}
    ):
        raise ValueError("outputs must stay outside repositories")
    manifest = json.loads(manifest_path.read_text())
    path = Path(manifest["baseline_manifest_path"])
    _read_hashed(path, manifest["baseline_manifest_sha256"])
    series, calendars, _ = read_bundle(path)
    audit, levels = audit_pair(
        series["H00300.CSI"],
        series["NHCI.NH"],
        calendars["SSE"],
        calendars["SHFE"],
        pd.Timestamp("2006-12-29"),
        pd.Timestamp("2025-12-31"),
    )
    if not audit["eligible"]:
        raise ValueError("baseline audit failed")
    exports, _ = read_exports(manifest["exports"])
    calendar = calendars["SSE"].intersection(calendars["SHFE"])
    endpoints = _endpoints(calendar, levels)
    rates = _series(exports[("shibor", None)], "date", "on")
    products, private = product_cases(levels, calendar, endpoints, rates, exports)
    training_audit, training = audit_pair(
        series["H00300.CSI"],
        series["NHCI.NH"],
        calendars["SSE"],
        calendars["SHFE"],
        pd.Timestamp("2006-01-30"),
        pd.Timestamp("2025-12-31"),
    )
    if not training_audit["eligible"]:
        raise ValueError("extended training calendar audit failed")
    training_ends = _endpoints(calendar, training)
    result = {
        "schema_version": 1,
        "study_id": "china_commodity_equity",
        "phase": "product_sensitivity_and_forward_registration",
        "source_revision": manifest["source_revision"],
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "code_sha256": {
            n: hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
            for n in ["forward_run.py", "funded_products.py"]
        },
        "products": products,
        "sensitivity": sensitivities(training, training_ends, rates),
        "training_audit": training_audit,
    }
    output.mkdir(parents=True)
    (output / "reviewed-candidate.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    (output / "private-ledgers.json").write_text(
        json.dumps(private, indent=2, allow_nan=False) + "\n"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_forward(args.manifest, args.output)


if __name__ == "__main__":
    main()
