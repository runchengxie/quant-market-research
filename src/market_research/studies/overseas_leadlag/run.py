"""Run retrospective diagnostics from external daily histories."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .models import paired_summary, walk_forward
from .proxy import adjusted_etf, simulate
from .timing import align_external, assumed_available, load_daily, validate_prices


def prepare(target, csi, sources, lag):
    frame, audit = align_external(target, sources, lag)
    ret = target.close.pct_change(fill_method=None)
    frame["own_lag"] = ret.shift(1)
    frame["own_mom5"] = target.close.pct_change(5, fill_method=None).shift(1)
    frame["own_vol20"] = ret.rolling(20).std().shift(1)
    controls = csi[["date", "close"]].copy()
    controls["available_utc"] = controls.date.map(lambda d: assumed_available(d, "domestic"))
    controls["csi_lag"] = controls.close.pct_change(fill_method=None)
    controls["csi_mom5"] = controls.close.pct_change(5, fill_method=None)
    aligned = pd.merge_asof(frame[["decision_utc"]], controls, left_on="decision_utc",
                            right_on="available_utc", direction="backward")
    frame[["csi_lag", "csi_mom5"]] = aligned[["csi_lag", "csi_mom5"]]
    return frame, audit


def targets(index_root, extra_root):
    csi = load_daily(index_root / "000300_sh_tushare_daily.csv")
    semis = load_daily(index_root / "801081_si_sw_daily.csv")
    sources = {}
    quality = {}
    for name in ["hsi", "n225", "ks11", "spx"]:
        data = load_daily(index_root / f"{name}_tushare_daily.csv")
        validate_prices(data, ["close"])
        sources[name] = (data, name, "close")
    for name, code in [("cnh", "usdcnh"), ("jpy", "usdjpy"), ("eur", "eurusd")]:
        data = load_daily(extra_root / f"{code}_fxcm_fx_daily.csv")
        validate_prices(data, ["bid_close", "ask_close"])
        crossed = data.ask_close < data.bid_close
        quality[name] = {"source_rows": len(data), "crossed_quotes_excluded": int(crossed.sum())}
        data = data.loc[~crossed].copy()
        data["mid"] = (data.bid_close + data.ask_close) / 2
        sources[name] = (data, "fx", "mid")
    result = {"csi300": csi, "sw_semiconductor": semis}
    for code in ["510300", "512480"]:
        bars = load_daily(extra_root / f"{code}_sh_fund_daily.csv")
        factors = load_daily(extra_root / f"{code}_sh_fund_adj.csv")
        validate_prices(bars, ["open", "close", "pre_close"])
        data = adjusted_etf(bars, factors)
        expected = csi.loc[(csi.date >= bars.date.min()) & (csi.date <= bars.date.max()), "date"]
        missing = set(expected) - set(bars.date)
        known = {pd.Timestamp("2021-03-26")} if code == "512480" else set()
        if missing - known:
            raise ValueError("Unexplained missing ETF sessions")
        quality[code] = {"bar_rows": len(bars), "factor_rows": len(factors),
                         "extra_factor_dates": int((~factors.date.isin(bars.date)).sum()),
                         "missing_bar_factors": int(data.adj_factor.isna().sum()),
                         "verified_suspension_dates": sorted(str(x.date()) for x in missing),
                         "unexplained_missing_sessions": 0}
        data["raw_close"] = data.close
        data["close"] = data.adjusted_close
        result[code] = data
    return result, sources, quality


def run(index_root, extra_root, output):
    repository = Path(__file__).resolve().parents[4]
    if output.resolve().is_relative_to(repository):
        raise ValueError("Research output must stay outside the source repository")
    output.mkdir(parents=True, exist_ok=False)
    data, sources, quality = targets(index_root, extra_root)
    comparisons, annual, costs, folds_all, audit_rows = [], [], [], [], []
    pairs = [("domestic_fx", "global"), ("global", "all_overseas"),
             ("domestic_fx", "all_overseas")]
    source_hashes = {}
    for root in [index_root, extra_root]:
        for path in sorted(root.glob("*.csv")):
            source_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    for name, target in data.items():
        is_etf = name in ["510300", "512480"]
        validate_prices(target, ["open", "close"])
        for lag in [0, 1]:
            base, audit = prepare(target, data["csi300"], sources, lag)
            audit["target"] = name
            audit["lag_sessions"] = lag
            audit_rows.append(audit)
            for outcome in (["next_tradable_open"] if is_etf else ["gap", "post_open"]):
                frame = base.copy()
                if outcome == "gap":
                    prev_close = target.pre_close if "pre_close" in target else target.close.shift(1)
                    frame["y"] = target.open / prev_close - 1
                    frame["label_end_utc"] = (
                        target.date.dt.tz_localize("Asia/Shanghai") + pd.Timedelta(hours=9, minutes=30)
                    ).dt.tz_convert("UTC")
                elif outcome == "post_open":
                    frame["y"] = target.close / target.open - 1
                    frame["label_end_utc"] = (
                        target.date.dt.tz_localize("Asia/Shanghai") + pd.Timedelta(hours=15)
                    ).dt.tz_convert("UTC")
                else:
                    frame["y"] = target.adjusted_open.shift(-1) / target.adjusted_open - 1
                    frame["label_end_utc"] = (
                        target.date.shift(-1).dt.tz_localize("Asia/Shanghai")
                        + pd.Timedelta(hours=9, minutes=30)
                    ).dt.tz_convert("UTC")
                    frame["exit_raw_open"] = target.open.shift(-1)
                    frame["exit_pre_close"] = target.auction_reference.shift(-1)
                forecasts, folds = walk_forward(frame)
                identity = {"target": name, "outcome": outcome, "lag_sessions": lag}
                folds_all.extend([{**identity, **fold} for fold in folds])
                forecasts.to_csv(output / f"{name}_{outcome}_lag{lag}_forecasts.csv", index=False)
                for b, a in pairs:
                    comparisons.append({**identity, **paired_summary(forecasts, b, a)})
                    for year, group in forecasts.groupby("fold"):
                        annual.append({**identity, "year": int(year),
                                       **paired_summary(group, b, a, bootstrap=250)})
                if not is_etf:
                    continue
                replay = frame[(frame.date >= forecasts.date.min())
                               & (frame.date <= forecasts.date.max())].copy()
                replay = replay.dropna(subset=["y", "exit_raw_open", "exit_pre_close"])
                for model in ["domestic_fx", "global", "all_overseas", "always_long"]:
                    prediction = (dict(zip(replay.date, [1.] * len(replay))) if model == "always_long"
                                  else dict(zip(forecasts.date, forecasts[model])))
                    for rt in [0, 5, 10, 20, 40]:
                        result, daily = simulate(replay, prediction, rt / 2)
                        costs.append({**identity, "model": model, "scenario": "flat_bps",
                                      "round_trip_bp": rt, **result})
                        if rt == 10:
                            pd.DataFrame({"date": replay.date, "return": daily}).to_csv(
                                output / f"{name}_{model}_lag{lag}_net10bp.csv", index=False)
                    for budget in [10000, 100000, 1000000]:
                        commission = max(3, 5 / budget * 10000)
                        for slip in [1, 5, 10]:
                            result, _ = simulate(replay, prediction, commission + slip, budget=budget)
                            costs.append({**identity, "model": model, "scenario": "budget",
                                          "commission_bp": commission, "slippage_one_way_bp": slip,
                                          **result})
    timing = pd.concat(audit_rows, ignore_index=True)
    timing.to_csv(output / "assumed_availability_rows.csv", index=False)
    timing_summary = {
        "rows": len(timing), "future_assumed_inputs": int(
            (timing.assumed_available_utc > timing.decision_utc).sum()),
        "historical_retrieval_verified_rows": 0,
        "stale_source_selections_over_10_days": int(timing.stale.sum()),
        "policy": "calendar-close-plus-one-hour; FX GMT day-end-plus-one-hour",
        "historical_pit_certified": False,
    }
    summary = {
        "schema_version": "overseas_leadlag_reviewed.v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_status": "retrospective_assumed_availability_daily_bar_proxy",
        "sample_end": str(max(frame.date.max() for frame in data.values()).date()),
        "source_sha256": source_hashes,
        "timing": timing_summary, "etf_input_quality": quality,
        "comparisons": comparisons, "annual": annual, "costs": costs, "folds": folds_all,
        "limitations": [
            "No historical retrieval vintages; assumed timing is not historical availability proof.",
            "Years previously inspected; annual folds are retrospective, not a new holdout.",
            "ETF opens are price proxies; fills, spreads, lot rounding, impact, cash distributions and capacity are not fully replayed.",
            "Selected extant ETFs have selection bias; 512480 tracks a different index from the SW industry target.",
            "512480 was suspended for a split on 2021-03-26: next tradable open may be later than the next A-share session. Annualized statistics use a 252-observed-interval approximation.",
            "No same-day domestic equity ETF round trip is claimed; ordinary shares are held until at least the next session open.",
            "Block-bootstrap intervals are descriptive, with no familywise multiple-testing correction.",
            "Budget and liquidity gates use fixed reference notionals, not the evolving equity of a growing account.",
        ],
    }
    (output / "reviewed_summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output": str(output), "comparisons": len(comparisons),
                      "annual_rows": len(annual), "cost_scenarios": len(costs),
                      "timing": timing_summary, "etf_quality": quality}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-inputs", type=Path, required=True)
    parser.add_argument("--extra-inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True,
                        help="New task directory outside the source repository")
    args = parser.parse_args()
    run(args.index_inputs, args.extra_inputs, args.output)


if __name__ == "__main__":
    main()
