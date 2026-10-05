"""Ad hoc, read-only TuShare screen; caches and artifacts in external run directory."""

import os
import json
import time
import hashlib
import argparse
import tomllib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import numpy as np
import requests
import threading
from market_research.dividend_screen import restated_dividend_events

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("mode", choices=["download", "base", "history", "volatility"])
parser.add_argument("--workspace-config", type=Path)
parser.add_argument("--source-root", type=Path)
parser.add_argument("--output-dir", type=Path)
parser.add_argument("--as-of", default="20261005")
parser.add_argument("--years", type=int, nargs="+", default=[2023, 2024, 2025])
args = parser.parse_args()
if args.years != [2023, 2024, 2025]:
    parser.error("this study is the fixed 2023-2025 slice; do not mix other years into its cache")
try:
    as_of_date = pd.to_datetime(args.as_of, format="%Y%m%d", errors="raise")
except ValueError:
    parser.error("--as-of must be YYYYMMDD")
if as_of_date < pd.Timestamp("2025-12-31"):
    parser.error("--as-of must be at least 20251231 for this complete-year retrospective study")
settings = tomllib.loads(args.workspace_config.read_text()) if args.workspace_config else {}
data_root = Path(settings["DATA_ROOT"]) if "DATA_ROOT" in settings else None
ROOT = args.source_root or (
    data_root / "quant/quant-market-data-platform/assets/tushare/a_share" if data_root else None
)
OUT = args.output_dir or (
    data_root / "quant/quant-market-research/dividend-screen/runs" / args.as_of
    if data_root
    else None
)
if ROOT is None or OUT is None:
    parser.error("provide --workspace-config, or both --source-root and --output-dir")
OUT.mkdir(parents=True, exist_ok=True)
CACHE = OUT / "raw"
CACHE.mkdir(exist_ok=True)
YEARS = args.years
REQUEST_LOCK = threading.Lock()
NEXT_REQUEST = 0.0


def api(name, params, fields="", secondary=False):
    global NEXT_REQUEST
    key = hashlib.sha256(
        json.dumps([name, params, fields, secondary], sort_keys=True).encode()
    ).hexdigest()[:20]
    path = CACHE / f"{name}_{key}.parquet"
    if path.exists():
        return pd.read_parquet(path)
    suffix = "_2" if secondary else ""
    for attempt in range(4):
        try:
            with REQUEST_LOCK:
                delay = max(0, NEXT_REQUEST - time.monotonic())
                if delay:
                    time.sleep(delay)
                NEXT_REQUEST = time.monotonic() + 0.36
            r = requests.post(
                os.environ.get("TUSHARE_API_URL" + suffix, "https://api.tushare.pro"),
                json={
                    "api_name": name,
                    "token": os.environ["TUSHARE_TOKEN" + suffix],
                    "params": params,
                    "fields": fields,
                },
                timeout=45,
            ).json()
            if r.get("code") != 0:
                raise RuntimeError(str(r.get("code")) + " " + str(r.get("msg")))
            d = pd.DataFrame(r["data"]["items"], columns=r["data"]["fields"])
            if r["data"].get("has_more") or len(d) >= 2000 and name == "dividend":
                raise RuntimeError("possible truncated response")
            d.to_parquet(path, index=False)
            (CACHE / f"{name}_{key}.query.json").write_text(
                json.dumps(
                    {
                        "api": name,
                        "params": params,
                        "fields": fields,
                        "rows": len(d),
                        "retrieved_at": pd.Timestamp.now(tz="UTC").isoformat(),
                    },
                    ensure_ascii=False,
                )
            )
            return d
        except Exception:
            if attempt == 3:
                raise
            time.sleep(1 + attempt * 2)


def download_dividends():
    # Query each calendar day, including holidays: full event-date population.
    days = [
        day
        for year in YEARS
        for day in pd.date_range(f"{year}-01-01", f"{year}-12-31").strftime("%Y%m%d").tolist()
    ]
    failures = []
    frames = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs = {pool.submit(api, "dividend", {"ex_date": day}): day for day in days}
        for n, f in enumerate(as_completed(jobs), 1):
            try:
                frames.append(f.result())
            except Exception as e:
                failures.append({"date": jobs[f], "error": str(e)})
            if n % 100 == 0:
                print("dividend dates", n, "/", len(days), "failures", len(failures), flush=True)
    pd.DataFrame(failures).to_csv(OUT / "download_failures.csv", index=False)
    if failures:
        raise RuntimeError("Dividend date queries incomplete; see failures")
    d = pd.concat([f for f in frames if not f.empty], ignore_index=True).drop_duplicates()
    d.to_parquet(OUT / "implemented_dividends_2023_2025.parquet", index=False)
    print("dividends downloaded", len(d), d.ts_code.nunique(), flush=True)


def annual_financials():
    root = ROOT / "normalized_fundamentals/a_share_all_normalized_fundamentals_latest/components"
    specs = {
        "income": ["total_revenue", "revenue", "n_income_attr_p", "basic_eps", "comp_type"],
        "balancesheet": ["total_assets", "total_liab", "total_hldr_eqy_exc_min_int", "total_share"],
        "cashflow": ["n_cashflow_act", "free_cashflow", "c_pay_acq_const_fiolta"],
        "fina_indicator": [
            "eps",
            "roe",
            "roe_waa",
            "roa",
            "debt_to_assets",
            "netprofit_yoy",
            "tr_yoy",
            "ocfps",
            "bps",
        ],
    }
    out = None
    for name, cols in specs.items():
        path = root / name / "data/part.parquet"
        dates = ["ts_code", "end_date", "ann_date"]
        if name != "fina_indicator":
            dates += ["f_ann_date", "report_type"]
        d = pd.read_parquet(path, columns=dates + cols)
        d = d[d.end_date.isin([str(y) + "1231" for y in YEARS]) & d.ann_date.le(args.as_of)].copy()
        if "report_type" in d:
            # Prefer consolidated adjusted statement type 4/5 over consolidated original type 1.
            d = d[d.report_type.isin(["1", "4", "5"])].copy()
            d["priority"] = d.report_type.map({"1": 1, "4": 2, "5": 3})
        else:
            d["priority"] = 1
        d = d.sort_values(["ts_code", "end_date", "ann_date", "priority"]).drop_duplicates(
            ["ts_code", "end_date"], keep="last"
        )
        d["year"] = d.end_date.str[:4].astype(int)
        d = d[["ts_code", "year", "ann_date"] + cols].rename(
            columns={"ann_date": name + "_ann_date", "total_share": "financial_total_share"}
        )
        out = (
            d
            if out is None
            else out.merge(d, on=["ts_code", "year"], how="outer", validate="one_to_one")
        )
    out["revenue_cny"] = out.total_revenue.combine_first(out.revenue)
    return out


def basic_at_year_end(year):
    root = ROOT / "daily_basic/a_share_all_daily_basic_latest/data"
    paths = sorted(root.glob(f"trade_date={year}12*/part.parquet"), reverse=True)
    frames = [pd.read_parquet(p) for p in paths]
    d = (
        pd.concat(frames, ignore_index=True)
        .sort_values("trade_date")
        .drop_duplicates("ts_code", keep="last")
    )
    d["year"] = year
    d["price_stale_days"] = (pd.Timestamp(f"{year}-12-31") - pd.to_datetime(d.trade_date)).dt.days
    # Preserve true last close even if a company was suspended throughout December.
    older = sorted(root.glob(f"trade_date={year}*/part.parquet"), reverse=True)
    instruments = pd.read_parquet(ROOT / "instruments/a_share_all_instruments_latest.parquet")
    need = set(
        instruments.loc[
            instruments.list_date.le(f"{year}1231")
            & (instruments.delist_date.isna() | instruments.delist_date.gt(f"{year}1231")),
            "ts_code",
        ]
    ) - set(d.ts_code)
    additions = []
    for p in older:
        if not need:
            break
        x = pd.read_parquet(p)
        x = x[x.ts_code.isin(need)]
        if len(x):
            additions.append(x)
            need -= set(x.ts_code)
    if additions:
        d = pd.concat([d, *additions], ignore_index=True).drop_duplicates("ts_code")
        d["year"] = year
        d["price_stale_days"] = (
            pd.Timestamp(f"{year}-12-31") - pd.to_datetime(d.trade_date)
        ).dt.days
    return d


def build_base():
    inst = pd.read_parquet(ROOT / "instruments/a_share_all_instruments_latest.parquet")
    inst = inst[inst.ts_code.str.endswith((".SH", ".SZ", ".BJ"))].drop_duplicates("ts_code")
    fin = annual_financials()
    fin.to_parquet(OUT / "annual_financials.parquet", index=False)
    members = pd.read_parquet(
        ROOT / "sw_industry_member/a_share_all_sw_industry_member_latest/data/part.parquet"
    )
    div = pd.read_parquet(OUT / "implemented_dividends_2023_2025.parquet")
    div = div[
        div.div_proc.eq("实施") & div.ex_date.notna() & (div.cash_div_tax.ge(0) | div.stk_div.gt(0))
    ].copy()
    div = div[
        div.ex_date.le(args.as_of) & (div.imp_ann_date.isna() | div.imp_ann_date.le(args.as_of))
    ].copy()
    div.loc[div.cash_div_tax.isna() & div.stk_div.gt(0), "cash_div_tax"] = 0.0
    div.loc[div.ts_code.eq("689009.SH"), "cash_div_tax"] /= 10
    div = div.merge(
        inst[["ts_code", "list_date"]], on="ts_code", how="inner", validate="many_to_one"
    )
    preipo = div[div.ex_date.lt(div.list_date)].copy()
    preipo.to_csv(OUT / "excluded_prelisting_dividends.csv", index=False, encoding="utf-8-sig")
    div = div[div.ex_date.ge(div.list_date)].copy()
    # Reviewed issuer announcements: public holder rate; combined ordinary/special event.
    overrides = [
        {
            "ts_code": "600989.SH",
            "end_date": "20231231",
            "ex_date": "20240724",
            "cash_div_tax": 0.3158,
            "reason": "Public minority-shareholder rate; major holder rate is 0.2650",
            "source": "https://file.finance.sina.com.cn/211.154.219.97%3A9494/MRGG/CNSESH_STOCK/2024/2024-7/2024-07-18/10334213.PDF",
        },
        {
            "ts_code": "002352.SZ",
            "end_date": "20240630",
            "ex_date": "20241107",
            "cash_div_tax": 1.4,
            "reason": "Combined interim 0.4 and special 1.0; do not sum duplicate combined row",
            "source": "https://www.hkexnews.hk/listedco/listconews/sehk/2025/0422/2025042200268_c.pdf",
        },
    ]
    for o in overrides:
        mask = (
            div.ts_code.eq(o["ts_code"])
            & div.end_date.eq(o["end_date"])
            & div.ex_date.eq(o["ex_date"])
        )
        div.loc[mask, "cash_div_tax"] = o["cash_div_tax"]
    pd.DataFrame(overrides).to_csv(
        OUT / "reviewed_event_overrides.csv", index=False, encoding="utf-8-sig"
    )
    keys = ["ts_code", "end_date", "ex_date", "record_date"]
    conflicts = div.groupby(keys, dropna=False).cash_div_tax.nunique()
    if conflicts.gt(1).any():
        raise RuntimeError("Conflicting dividends require review")
    div = div.sort_values("imp_ann_date").drop_duplicates(keys, keep="last")
    div["year"] = div.ex_date.str[:4].astype(int)
    cash_year = div.groupby(["ts_code", "year"]).cash_div_tax.transform("sum").gt(0)
    div.loc[~cash_year].to_csv(OUT / "stock_only_actions.csv", index=False, encoding="utf-8-sig")
    div = div.loc[cash_year].copy()
    div = div.sort_values(["ts_code", "year", "ex_date"])
    div = restated_dividend_events(div)
    agg = (
        div.groupby(["ts_code", "year"])
        .agg(
            cash_div=("cash_div_tax", "sum"),
            nominal_cash_div=("cash_div_tax_raw", "sum"),
            dividend_events=("cash_div_tax", "size"),
            first_ex_date=("ex_date", "min"),
            last_ex_date=("ex_date", "max"),
            stock_div=("stk_div", "sum"),
        )
        .reset_index()
    )
    div.to_csv(OUT / "dividend_events.csv", index=False, encoding="utf-8-sig")
    frames = []
    for year in YEARS:
        d = basic_at_year_end(year)
        d = d.merge(
            inst[["ts_code", "name", "industry", "list_date", "delist_date"]],
            on="ts_code",
            how="inner",
            validate="one_to_one",
        )
        d = d[
            d.list_date.le(f"{year}1231") & (d.delist_date.isna() | d.delist_date.gt(f"{year}1231"))
        ].copy()
        m = (
            members[
                members.in_date.le(f"{year}1231")
                & (members.out_date.isna() | members.out_date.gt(f"{year}1231"))
            ]
            .sort_values("in_date")
            .drop_duplicates("con_code", keep="last")
        )
        d = d.merge(
            m[["con_code", "industry_name"]],
            left_on="ts_code",
            right_on="con_code",
            how="left",
            validate="one_to_one",
        )
        d["industry_name"] = d.industry_name.fillna("未分类")
        d = d.merge(fin, on=["ts_code", "year"], how="left", validate="one_to_one")
        d["is_broker"] = d.industry.eq("证券") | d.comp_type.eq("4")
        d.loc[d.is_broker & d.industry.isna(), "industry"] = "证券"
        d["head_group"] = np.where(d.is_broker, "证券", d.industry_name)
        d["industry_mv_rank"] = d.groupby("head_group").total_mv.rank(method="min", ascending=False)
        d["industry_members"] = d.groupby("head_group").ts_code.transform("size")
        d["head_proxy"] = np.where(
            d.industry_mv_rank.le(3) & d.industry_name.ne("未分类"), "是（行业年末市值前三）", "否"
        )
        d = d.merge(agg, on=["ts_code", "year"], how="left", validate="one_to_one")
        d[["cash_div", "dividend_events"]] = d[["cash_div", "dividend_events"]].fillna(0)
        d["yield_pct"] = d.cash_div / d.close * 100
        d["market"] = "A"
        d["a_code"] = d.ts_code
        frames.append(d)
    allrows = pd.concat(frames, ignore_index=True)
    allrows.to_parquet(OUT / "a_all_years_base.parquet", index=False)
    selected = allrows[allrows.yield_pct.gt(5)].copy()
    selected.to_csv(OUT / "a_selected_base.csv", index=False, encoding="utf-8-sig")
    print(
        "A annual universe",
        allrows.groupby("year").size().to_dict(),
        "selected",
        selected.groupby("year").size().to_dict(),
        flush=True,
    )
    return allrows


def enrich_dividend_history():
    d = pd.read_parquet(OUT / "a_all_years_base.parquet")
    codes = set(d.loc[d.yield_pct.gt(5), "ts_code"]) | {"002736.SZ"}
    mapping = OUT / "ah_mapping.csv"
    if mapping.exists():
        codes |= set(pd.read_csv(mapping).a_code)
    fields = "ts_code,end_date,ann_date,div_proc,stk_div,cash_div_tax,record_date,ex_date,pay_date,imp_ann_date,base_date,base_share"
    frames = []
    failed = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs = {
            pool.submit(api, "dividend", {"ts_code": code}, fields): code for code in sorted(codes)
        }
        for n, f in enumerate(as_completed(jobs), 1):
            try:
                frames.append(f.result())
            except Exception as e:
                failed.append({"ts_code": jobs[f], "error": str(e)})
            if n % 100 == 0:
                print("dividend history", n, "/", len(codes), flush=True)
    pd.concat([f for f in frames if not f.empty], ignore_index=True).to_parquet(
        OUT / "selected_dividend_history.parquet", index=False
    )
    pd.DataFrame(failed).to_csv(OUT / "history_failures.csv", index=False)
    print("history complete failures", len(failed), flush=True)
    if failed:
        raise RuntimeError("dividend histories incomplete; retry before exporting")


def volatility():
    d = pd.read_parquet(OUT / "a_all_years_base.parquet")
    codes = set(d.loc[d.yield_pct.gt(5), "ts_code"]) | {"002736.SZ"}
    parts = []
    for year in YEARS:
        dailyroot = ROOT / "daily/a_share_all_daily_latest/data"
        adjroot = ROOT / "adj_factor/a_share_all_adj_factor_latest/data"
        dates = sorted(dailyroot.glob(f"trade_date={year}*/part.parquet"))
        previous = sorted(dailyroot.glob(f"trade_date={year - 1}*/part.parquet"))[-1:]
        frames = []
        for p in previous + dates:
            x = pd.read_parquet(p, columns=["ts_code", "trade_date", "close", "pct_chg", "vol"])
            x = x[x.ts_code.isin(codes)]
            ap = adjroot / p.parent.name / "part.parquet"
            if not ap.exists():
                x["adj_factor"] = np.nan
            else:
                a = pd.read_parquet(ap, columns=["ts_code", "adj_factor"])
                x = x.merge(a, on="ts_code", how="left", validate="one_to_one")
            frames.append(x)
        x = pd.concat(frames).sort_values(["ts_code", "trade_date"])
        # Include first annual return using previous year's last adjusted close.
        x["adjusted_close"] = x.close * x.adj_factor
        g = x.groupby("ts_code", sort=False)
        x["return"] = g.adjusted_close.pct_change(fill_method=None)
        x["prev_date"] = g.trade_date.shift()
        x["gap_days"] = (pd.to_datetime(x.trade_date) - pd.to_datetime(x.prev_date)).dt.days
        x = x[x.trade_date.str.startswith(str(year))].copy()
        v = x.groupby("ts_code").agg(
            returns_n=("return", "count"),
            volatility_pct=("return", lambda s: s.std(ddof=1) * np.sqrt(252) * 100),
            max_gap_days=("gap_days", "max"),
            zero_volume_days=("vol", lambda s: (s <= 0).sum()),
            missing_adj=("adj_factor", lambda s: s.isna().sum()),
        )
        v["year"] = year
        parts.append(v.reset_index())
        print("volatility", year, len(v), "daily partitions", len(dates), flush=True)
    pd.concat(parts).to_parquet(OUT / "a_volatility.parquet", index=False)


if __name__ == "__main__":
    if args.mode == "download":
        download_dividends()
    elif args.mode == "base":
        build_base()
    elif args.mode == "history":
        enrich_dividend_history()
    elif args.mode == "volatility":
        volatility()
