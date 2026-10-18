#!/usr/bin/env python3
"""Prepare SH/SZ-only publication and measure retrospective lifecycle sensitivity.

Raw features and lifecycle masters stay external. Only aggregate proposal files
are emitted; publish the main and relative proposals through their review gates.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import date
from pathlib import Path

import duckdb

from market_research.liquidity_rebuild import summarize_period
from market_research.liquidity_universe import lifecycle_screen, scenario_stock_limits


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--trial", type=Path, required=True)
    p.add_argument("--features", type=Path, required=True)
    p.add_argument("--master", type=Path, nargs="+", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    repo = Path(__file__).resolve().parents[1]
    if args.output.resolve().is_relative_to(repo):
        raise ValueError("outputs must stay external")
    args.output.mkdir(parents=True, exist_ok=True)
    old = json.loads(args.base.read_text())
    trial = json.loads((args.trial / "summary.proposed.json").read_text())
    receipt = json.loads((args.trial / "run-receipt.json").read_text())
    feature = args.features / "features-A-share.parquet"
    assert sha(feature) == receipt["feature_sha256"]
    assert sha(args.trial / "summary.proposed.json") == receipt["summary_sha256"]
    result = copy.deepcopy(old)
    result["generated_on"] = date.today().isoformat()
    result["markets"] = [
        next(m for m in trial["latest_markets"] if m["market"] == x["market"])
        if x["market"] == "A-share"
        else x
        for x in result["markets"]
    ]
    for period in result["periods"]:
        replacement = next(x for x in trial["periods"] if x["period"] == period["period"])
        assert (period["common_start"], period["common_end"], period["common_dates"]) == (
            replacement["common_start"],
            replacement["common_end"],
            replacement["common_dates"],
        )
        period["markets"] = [
            next(m for m in replacement["markets"] if m["market"] == "A-share")
            if x["market"] == "A-share"
            else x
            for x in period["markets"]
        ]
    profile = trial["source_profile"]
    result["source_profiles"]["A-share"] = dict(
        source_rows=profile["source_rows"],
        observed_stocks=profile["observed_stocks"],
        coverage_start=profile["coverage_start"],
        coverage_end=profile["coverage_end"],
        eligible_observations=profile["eligible_feature_rows"],
        exclusions=profile["feature_exclusions"],
        duplicate_keys=profile["duplicate_keys"],
    )
    result["code_receipts"]["scope_builder"] = sha(Path(__file__))
    result["code_receipts"]["scope_rules"] = sha(repo / "src/market_research/liquidity_universe.py")
    result["source_receipts"].append(
        dict(
            source_id="a_sh_sz_features", files=1, bytes=feature.stat().st_size, sha256=sha(feature)
        )
    )
    result["caveats"].append(
        "A股仅含沪深，排除北交所和已确认的前身代码；本地日线始于2015年，跨市场比较从2020年起。"
    )
    write(args.output / "summary.proposed.json", result)
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.execute("SET memory_limit='2GB'")
    paths = [str(args.features / f"features-{m['market']}.parquet") for m in result["markets"]]
    con.read_parquet(paths).create_view("features")
    con.read_parquet(str(feature)).create_view("a_features")
    con.read_parquet([str(m) for m in args.master]).create_view("master_raw")
    con.execute(
        "CREATE VIEW master AS SELECT ts_code symbol,try_strptime(list_date,'%Y%m%d')::DATE list_date,try_strptime(delist_date,'%Y%m%d')::DATE delist_date FROM master_raw"
    )
    lifecycle_screen(con, "a_features", "master", "screened")
    views = [
        dict(
            period="latest",
            included_markets=[m["market"]],
            common_start=m["as_of"],
            common_end=m["as_of"],
            common_dates=1,
            markets=[m],
        )
        for m in result["markets"]
    ] + result["periods"]
    limits = []
    sensitivity = []
    scope = []
    for view in views:
        limits.append(
            dict(
                period=view["period"],
                common_start=view["common_start"],
                common_end=view["common_end"],
                markets=scenario_stock_limits(con, "features", view),
            )
        )
        a = next((m for m in view["markets"] if m["market"] == "A-share"), None)
        if a is None:
            continue
        # Preserve the published multi-market calendar in both sensitivity variants.
        marks = view["included_markets"]
        ps = ",".join("?" for _ in marks)
        con.execute(
            f"CREATE OR REPLACE TEMP TABLE shared_dates AS SELECT date FROM features WHERE eligible AND date BETWEEN ?::DATE AND ?::DATE AND market IN ({ps}) GROUP BY date HAVING count(DISTINCT market)=?",
            [view["common_start"], view["common_end"], *marks, len(marks)],
        )
        con.execute(
            "CREATE OR REPLACE VIEW screened_shared AS SELECT s.* FROM screened s JOIN shared_dates USING(date)"
        )
        screened = summarize_period(
            con,
            "screened_shared",
            date.fromisoformat(view["common_start"]),
            date.fromisoformat(view["common_end"]),
            ["A-share"],
        )
        assert screened["common_dates"] == view["common_dates"]
        b = screened["markets"][0]
        sensitivity.append(
            dict(
                period=view["period"],
                common_start=view["common_start"],
                common_end=view["common_end"],
                common_dates=view["common_dates"],
                base=a,
                lifecycle=b,
            )
        )
        prior = (
            next(m for m in old["markets"] if m["market"] == "A-share")
            if view["period"] == "latest"
            else next(
                m
                for m in next(p for p in old["periods"] if p["period"] == view["period"])["markets"]
                if m["market"] == "A-share"
            )
        )
        scope.append(dict(period=view["period"], previous_including_bse=prior, sh_sz=a))
    summary = dict(
        schema_version="liquidity.universe-sensitivity.v1",
        historical_pit_eligible=False,
        method="SH/SZ only; compare eligible historical bars against current stock_basic lifecycle intervals at the prior market session. Listing inclusive; delisting exclusive. Unknown lifecycle dates excluded. Retrospective cross-check, not historical PIT certification.",
        master_receipts=[dict(sha256=sha(m), bytes=m.stat().st_size) for m in args.master],
        feature_sha256=sha(feature),
        periods=sensitivity,
        scope_changes=scope,
    )
    write(args.output / "universe-sensitivity.json", summary)
    write(
        args.output / "scenario-limits.json",
        dict(
            schema_version="liquidity.scenario-limits.v1",
            absolute_summary_sha256=sha(args.output / "summary.proposed.json"),
            method="Minimum daily eligible stock count on exact published common dates; empty bucket-days count as zero. Relative quintiles follow NTILE(5).",
            views=limits,
        ),
    )
    print(
        json.dumps(
            {
                "periods": [
                    (
                        x["period"],
                        x["base"]["eligible_observations"],
                        x["lifecycle"]["eligible_observations"],
                    )
                    for x in sensitivity
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
