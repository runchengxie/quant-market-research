"""Run five finite decision-risk studies on frozen external asset inputs.

Never fetches data, modifies production aliases, or admits prospective outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import gettempdir

import numpy as np
import pandas as pd

from market_research.studies.asset_returns.analysis import validate_levels
from market_research.studies.asset_returns.etf import etf_gap
from market_research.studies.asset_returns.inputs import read_frozen_response, month_end_levels
from market_research.studies.asset_returns.investability import (
    launch_split,
    round_trip_cagr,
    validate_register,
)
from market_research.studies.asset_returns.spending import spending_path, summarize_spending
from market_research.studies.asset_returns.stress import conditional_stress, event_recovery
from market_research.studies.asset_returns.uncertainty import paired_uncertainty, policy_wealth

PORTFOLIOS = {
    "equity_only": [1.0, 0.0, 0.0],
    "stock_bond_60_40": [0.6, 0.4, 0.0],
    "stock_bond_gold_equal": [1 / 3, 1 / 3, 1 / 3],
}
LAUNCHES = {
    "all_share": ("000985", "2011-08-02"),
    "large_cap": ("000300", "2005-04-08"),
    "small_cap": ("000852", "2014-10-17"),
}
EVENTS = [
    ("2008", "2007-12-31", "2009-12-31"),
    ("2015", "2015-05-31", "2016-12-31"),
    ("2020", "2019-12-31", "2020-12-31"),
    ("2022", "2021-12-31", "2022-12-31"),
]


def run(previous, previous_owner, robustness_owner, followup, owner, output):
    if output.exists():
        raise FileExistsError("select a new output directory")
    if any(
        (p / ".git").exists()
        for p in [output.resolve(), *output.resolve().parents]
        if p not in {Path.home(), Path(gettempdir())}
    ):
        raise ValueError("full results belong outside repositories")
    sources = []
    repo = Path(__file__).resolve().parents[1]
    followup_blob = (followup / "results.json").read_bytes()
    reviewed_public = json.loads(
        (repo / "web/public/data/asset_robustness_reviewed.json").read_text()
    )
    if hashlib.sha256(followup_blob).hexdigest() != reviewed_public["result_sha256"]:
        raise ValueError("follow-up run differs from reviewed release")
    sources.append({"id": "reviewed_followup", "sha256": hashlib.sha256(followup_blob).hexdigest()})
    inputs = {}
    for name in ["all_share", "large_cap", "small_cap", "multi_asset"]:
        path = previous / "inputs" / (name + ".csv")
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        frozen = json.loads((previous / "runs" / name / "results.json").read_text())
        if frozen["provenance"]["input_sha256"] != digest:
            raise ValueError("frozen first-round input changed")
        sources.append({"id": name, "sha256": digest})
        inputs[name] = pd.read_csv(path)
    multi = validate_levels(inputs["multi_asset"], ["total", "bond", "gold", "cpi"])
    paired = validate_levels(inputs["small_cap"], ["total", "benchmark"])
    m_returns = multi[["total", "bond", "gold"]].pct_change(fill_method=None).iloc[1:].to_numpy()
    p_returns = paired[["total", "benchmark"]].pct_change(fill_method=None).iloc[1:].to_numpy()
    uncertainty = paired_uncertainty(m_returns, p_returns[:, 0], p_returns[:, 1])
    eras = []
    for lo, hi in [(2005, 2009), (2010, 2014), (2015, 2019), (2020, 2025)]:
        select = paired.date.iloc[1:].dt.year.between(lo, hi).to_numpy()
        rel = p_returns[select]
        mselect = multi.date.iloc[1:].dt.year.between(lo, hi).to_numpy()
        r = m_returns[mselect]
        hold = policy_wealth(r[None], [0.6, 0.4, 0.0], "buy_hold")[0]
        annual = policy_wealth(r[None], [0.6, 0.4, 0.0], "annual")[0]
        eras.append(
            {
                "id": f"{lo}-{hi}",
                "small_large_months": len(rel),
                "small_large_relative_cagr": float(
                    np.expm1((np.log1p(rel[:, 0]) - np.log1p(rel[:, 1])).mean() * 12)
                ),
                "allocation_months": len(r),
                "allocation_first_return_end": multi.date.iloc[1:][mselect]
                .iloc[0]
                .date()
                .isoformat(),
                "annual_minus_hold_cagr": float(
                    annual[-1] ** (12 / len(r)) - hold[-1] ** (12 / len(r))
                ),
            }
        )
    print("paired uncertainty and fixed eras complete", flush=True)
    details, spending = [], []
    horizon = 120
    # Only full windows; annual policy anniversaries reset at every formation.
    sleeve_returns = {}
    for ident, weights in PORTFOLIOS.items():
        sleeve_returns[ident] = []
        for start in range(len(m_returns) - horizon + 1):
            wealth = policy_wealth(m_returns[None, start : start + horizon], weights, "annual")[0]
            sleeve_returns[ident].append(wealth[1:] / wealth[:-1] - 1)
    for ident in PORTFOLIOS:
        for annual in [0, 2, 4, 6]:
            for buffer in [0, 12, 24]:
                for shock_month in [None, 12, 60]:
                    paths = []
                    for start, r in enumerate(sleeve_returns[ident]):
                        result = spending_path(
                            r,
                            multi.cpi.iloc[start : start + horizon + 1],
                            annual_real=annual,
                            buffer_months=buffer,
                            shock_month=shock_month,
                            shock_real=20 if shock_month else 0,
                        )
                        result["formation"] = multi.date.iloc[start].date().isoformat()
                        paths.append(result)
                    row = {
                        "portfolio": ident,
                        "annual_real_demand_per_initial_100": annual,
                        "cash_buffer_months": buffer,
                        "shock_month": shock_month,
                        "shock_real_per_initial_100": 20 if shock_month else 0,
                        "summary": summarize_spending(paths),
                    }
                    spending.append(row)
                    details.append({**row, "windows": paths})
    print("108 spending scenarios complete", flush=True)
    launch_sources = {x["id"]: x for x in json.loads((owner / "sources/receipt.json").read_text())}
    launches = {}
    for name, (code, date) in LAUNCHES.items():
        entry = launch_sources[code]
        blob = (owner / "sources" / (code + ".pdf")).read_bytes()
        if hashlib.sha256(blob).hexdigest() != entry["sha256"]:
            raise ValueError("official publication source changed")
        sources.append({"id": "official_" + code, **entry})
        launches[name] = launch_split(inputs[name], date)
        launches[name]["official_source_url"] = entry["url"]
        selected = inputs[name].copy()
        if "benchmark" in selected:
            selected = selected.loc[pd.to_datetime(selected.date) >= date]
            ratio = selected.total / selected.benchmark
            launches[name]["post_launch_relative_benchmark_cagr"] = float(
                (ratio.iloc[-1] / ratio.iloc[0]) ** (12 / (len(ratio) - 1)) - 1
            )

    # Read every used supplier response with its frozen receipt hash.
    def response(folder, ident):
        receipt = json.loads((folder / "receipt.json").read_text())
        row = next(x for x in receipt if x["id"] == ident)
        sources.append(
            {
                "id": folder.name + "/" + ident,
                "sha256": row.get("sha256"),
                "status": row.get("status"),
            }
        )
        return read_frozen_response(folder / (ident + ".json"), row["sha256"])

    calendar = response(previous_owner / "raw", "calendar")
    sessions = pd.DatetimeIndex(pd.to_datetime(calendar.cal_date))
    products = {}
    old_receipt = json.loads((robustness_owner / "raw/receipt.json").read_text())
    for code in ["510300.SH", "159919.SZ", "512100.SH"]:
        prefix = code.replace(".", "_")
        early_gaps = []
        try:
            basic = response(robustness_owner / "raw", prefix + "_basic").iloc[0]
            data = {}
            for api in ["fund_daily", "fund_adj", "fund_nav"]:
                chunks = [response(owner / "early-etf", prefix + "_" + api)]
                chunks += [
                    response(robustness_owner / "raw", x["id"])
                    for x in old_receipt
                    if x["api"] == api and x["params"].get("ts_code") == code
                ]
                data[api] = pd.concat(chunks, ignore_index=True)
            start = pd.Timestamp(basic.list_date).to_period("M").start_time
            cal = sessions[(sessions >= start) & (sessions <= "2025-12-31")]
            monthly = None
            for api, datecol, value in [
                ("fund_daily", "trade_date", "close"),
                ("fund_adj", "trade_date", "adj_factor"),
                ("fund_nav", "nav_date", "unit_nav"),
                ("fund_nav", "nav_date", "adj_nav"),
            ]:
                frame = (
                    data[api].rename(columns={datecol: "date", value: "close"})
                    if value != "close"
                    else data[api].rename(columns={datecol: "date"})
                )
                frame = frame[["date", "close"]].copy()
                frame["date"] = pd.to_datetime(frame.date)
                endpoints = pd.Series(cal, index=cal.to_period("M")).groupby(level=0).max()
                values = frame.set_index("date").reindex(pd.DatetimeIndex(endpoints.to_numpy()))
                bad = ~np.isfinite(pd.to_numeric(values.close, errors="coerce")) | (
                    values.close <= 0
                )
                if bad.any():
                    early_gaps.append(
                        {
                            "field": value,
                            "last_session_dates": values.index[bad].strftime("%Y-%m-%d").tolist(),
                        }
                    )
                    continue
                selected = month_end_levels(frame, cal).rename(columns={"close": value})
                monthly = (
                    selected
                    if monthly is None
                    else monthly.merge(selected, on="date", validate="one_to_one")
                )
            if early_gaps:
                raise ValueError("missing or invalid last-session quote")
            reference = inputs["small_cap" if code == "512100.SH" else "large_cap"][
                ["date", "total"]
            ].copy()
            reference["date"] = pd.to_datetime(reference.date)
            monthly = monthly.merge(
                reference.rename(columns={"total": "index_total"}), on="date", validate="one_to_one"
            )
            gap = etf_gap(monthly)
            growth = float(
                (monthly.close.iloc[-1] * monthly.adj_factor.iloc[-1])
                / (monthly.close.iloc[0] * monthly.adj_factor.iloc[0])
            )
            months = len(monthly) - 1
            products[code] = {
                "status": "observed_proxy",
                "list_date": pd.Timestamp(basic.list_date).date().isoformat(),
                "first_observed_month_end": monthly.date.iloc[0].date().isoformat(),
                "first_complete_return_month_end": monthly.date.iloc[1].date().isoformat(),
                "gap": gap,
                "round_trip_sensitivities": [
                    {
                        "cost_bps_per_side": fee,
                        "market_proxy_cagr_after_entry_exit": round_trip_cagr(growth, months, fee),
                    }
                    for fee in [0, 10, 50]
                ],
            }
            output.mkdir(parents=True, exist_ok=True)
            monthly.to_csv(output / (prefix + "_monthly.csv"), index=False)
        except (ValueError, KeyError, StopIteration) as exc:
            failure = str(exc)
            mature_path = followup / (prefix + "_monthly.csv")
            mature_blob = mature_path.read_bytes()
            mature = pd.read_csv(mature_path)
            mature_gap = etf_gap(mature)
            reviewed = json.loads((followup / "results.json").read_text())["etfs"][code]
            if any(
                (not np.isclose(mature_gap[key], reviewed[key], rtol=0, atol=1e-12))
                if isinstance(mature_gap[key], float)
                else mature_gap[key] != reviewed[key]
                for key in mature_gap
            ):
                raise ValueError("mature ETF proxy no longer matches frozen reviewed result")
            sources.append(
                {"id": "mature_" + prefix, "sha256": hashlib.sha256(mature_blob).hexdigest()}
            )
            growth = float(
                (mature.close.iloc[-1] * mature.adj_factor.iloc[-1])
                / (mature.close.iloc[0] * mature.adj_factor.iloc[0])
            )
            products[code] = {
                "status": "mature_proxy_only",
                "early_history_blocked_reason": failure,
                "early_month_end_gaps": early_gaps,
                "first_observed_month_end": mature.date.iloc[0],
                "first_complete_return_month_end": mature.date.iloc[1],
                "gap": mature_gap,
                "round_trip_sensitivities": [
                    {
                        "cost_bps_per_side": fee,
                        "market_proxy_cagr_after_entry_exit": round_trip_cagr(
                            growth, len(mature) - 1, fee
                        ),
                    }
                    for fee in [0, 10, 50]
                ],
            }
    yield_probes = json.loads((owner / "yield10/receipt.json").read_text())
    for probe in yield_probes:
        raw_blob = (owner / "yield10" / (probe["id"] + ".json")).read_bytes()
        if hashlib.sha256(raw_blob).hexdigest() != probe["sha256"] or json.loads(raw_blob).get(
            "code"
        ) != probe.get("code"):
            raise ValueError("yield availability response no longer matches its receipt")
        sources.append(
            {"id": "yield10/" + probe["id"], "sha256": probe["sha256"], "code": probe.get("code")}
        )
    repo = Path(__file__).resolve().parents[1]
    register_blob = (repo / "studies/asset_returns/conclusion-register.json").read_bytes()
    register = json.loads(register_blob)
    validate_register(register["claims"])
    files = [
        Path(__file__).resolve(),
        *sorted((repo / "src/market_research/studies/asset_returns").glob("*.py")),
    ]
    result = {
        "schema_version": 1,
        "sample": {
            "multi_start": str(multi.date.iloc[0].date()),
            "end": str(multi.date.iloc[-1].date()),
            "multi_return_months": len(m_returns),
            "paired_return_months": len(p_returns),
        },
        "uncertainty": uncertainty,
        "eras": eras,
        "spending": spending,
        "spending_details": details,
        "stress": conditional_stress(multi),
        "events": event_recovery(multi, EVENTS),
        "launches": launches,
        "products": products,
        "conclusion_register": register,
        "provenance": {
            "sources": sources,
            "code_sha256": {
                str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files
            },
            "register_sha256": hashlib.sha256(register_blob).hexdigest(),
        },
        "availability": {
            "ten_year_sovereign_yield": {
                "status": "not_admitted",
                "reason": "configured service denied yc_cb probes (40203); bond-return stress is not a yield-rise mask",
                "probes": [
                    {"id": r["id"], "code": r.get("code"), "sha256": r.get("sha256")}
                    for r in json.loads((owner / "yield10/receipt.json").read_text())
                ],
            }
        },
        "scope": "Conditional historical sensitivity; no prospective admission or future failure/return probability.",
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print("Frozen decision study complete", flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["previous", "previous-owner", "robustness-owner", "followup", "owner", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    a = parser.parse_args()
    run(a.previous, a.previous_owner, a.robustness_owner, a.followup, a.owner, a.output)
