import json
import pathlib
import concurrent.futures
import argparse
import re
import pandas as pd
import numpy as np
import requests

parser = argparse.ArgumentParser()
parser.add_argument(
    "mode",
    choices=["probe", "fetch", "output", "fallback", "audit", "tencent"],
    default="output",
    nargs="?",
)
parser.add_argument("--output-dir", required=True)
parser.add_argument("--a-instruments", required=True)
parser.add_argument("--h-instruments", required=True)
parser.add_argument("--h-delisted")
parser.add_argument(
    "--supplementary-dividends",
    help="CSV of independently sourced events: ts_code,date,amount,currency,source",
)
args = parser.parse_args()
ROOT = pathlib.Path(args.output_dir)
RAW = ROOT / "hk_raw"
RAW.mkdir(parents=True, exist_ok=True)
A_PATH = args.a_instruments


def write_csv_atomic(frame, path):
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False)
    temporary.replace(path)


def mapping():
    a = pd.read_parquet(A_PATH)
    h = pd.read_parquet(args.h_instruments)
    if args.h_delisted:
        h = pd.concat([h, pd.read_parquet(args.h_delisted)], ignore_index=True)
    # Full legal-name equality is deliberately conservative; no fuzzy parent/subsidiary match.
    m = a[a.fullname.notna()].merge(h[h.fullname.notna()], on="fullname", suffixes=("_a", "_h"))
    m = m[m.curr_type_h.eq("HKD") & m.ts_code_h.str[:1].ne("8")]
    m = pd.DataFrame(
        {
            "a_code": m.ts_code_a,
            "ts_code": m.ts_code_h,
            "name": m.name_h,
            "a_name": m.name_a,
            "fullname": m.fullname,
            "a_list_date": m.list_date_a,
            "a_delist_date": m.delist_date_a,
            "h_list_date": m.list_date_h,
            "h_delist_date": m.delist_date_h,
            "match_method": "exact_full_legal_name",
        }
    )
    m = m[
        (m.h_delist_date.isna() | m.h_delist_date.ge("20230101"))
        & (m.a_delist_date.isna() | m.a_delist_date.ge("20230101"))
    ].reset_index(drop=True)
    write_csv_atomic(m, ROOT / "ah_mapping.csv")
    print(
        "mapping",
        len(m),
        "HK listings;",
        len(m[m.h_list_date.le("20251231")]),
        "listed by 2025-end",
        flush=True,
    )
    return m


def chart(row):
    code = row["ts_code"]
    path = RAW / (code + ".json")
    if path.exists():
        obj = json.loads(path.read_text())
        if obj.get("chart", {}).get("result"):
            return code, "cached"
    symbol = str(int(code.split(".")[0])).zfill(4) + ".HK"
    params = {
        "period1": 1672358400,
        "period2": 1767225600,
        "interval": "1d",
        "events": "div,splits",
    }
    errors = []
    for host in ["query1.finance.yahoo.com", "query2.finance.yahoo.com"]:
        try:
            resp = requests.get(
                "https://" + host + "/v8/finance/chart/" + symbol,
                params=params,
                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
                timeout=20,
            )
            obj = resp.json()
            if resp.ok and obj.get("chart", {}).get("result"):
                obj["_fetch"] = {
                    "url": resp.url,
                    "fetched_at": pd.Timestamp.now(tz="UTC").isoformat(),
                    "symbol": symbol,
                }
                path.write_text(json.dumps(obj))
                return code, "ok"
            errors.append(str(resp.status_code) + ":" + str(obj.get("chart", {}).get("error")))
        except Exception as e:
            errors.append(str(e)[:160])
    (RAW / (code + ".error.json")).write_text(json.dumps({"symbol": symbol, "errors": errors}))
    return code, "failed " + str(errors)


def fallback(codes=None):
    for code in codes or ["01839", "06837"]:
        for kind in ["dividends", "prices", "adjusted_prices"]:
            try:
                if kind == "dividends":
                    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
                    params = {
                        "reportName": "RPT_HKF10_MAIN_DIVBASIC",
                        "columns": "ALL",
                        "filter": f'(SECURITY_CODE="{code}")(IS_BFP="0")',
                        "pageNumber": 1,
                        "pageSize": 200,
                        "sortTypes": "-1,-1",
                        "sortColumns": "NOTICE_DATE,EX_DIVIDEND_DATE",
                        "source": "F10",
                        "client": "PC",
                    }
                else:
                    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
                    params = {
                        "secid": "116." + code,
                        "klt": 101,
                        "fqt": 1 if kind == "adjusted_prices" else 0,
                        "beg": "20221230",
                        "end": "20251231",
                        "fields1": "f1,f2,f3,f4,f5,f6",
                        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                    }
                response = requests.get(
                    url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=25
                )
                obj = response.json()
                obj["_fetch"] = {"url": response.url, "source": "Eastmoney"}
                (RAW / (code + ".HK.eastmoney." + kind + ".json")).write_text(json.dumps(obj))
                data = obj.get("result", {})
                data = data.get("data", []) if data else obj.get("data")
                print(code, kind, response.status_code, str(data)[:300], flush=True)
            except Exception as e:
                print(code, kind, str(e)[:120], flush=True)


def output(m):
    out = []
    gaps = []
    events = []
    splits = []
    for row in m.to_dict("records"):
        eligible_years = [
            year
            for year in [2023, 2024, 2025]
            if str(row["h_list_date"]) <= str(year) + "1231"
            and (pd.isna(row["h_delist_date"]) or str(row["h_delist_date"]) > str(year) + "1231")
            and str(row["a_list_date"]) <= str(year) + "1231"
            and (pd.isna(row["a_delist_date"]) or str(row["a_delist_date"]) > str(year) + "1231")
        ]
        if not eligible_years:
            continue
        path = RAW / (row["ts_code"] + ".json")
        if not path.exists():
            if supplementary_output(row, eligible_years, out, events):
                continue
            gaps.extend(
                {**row, "year": year, "reason": "Yahoo chart unavailable"}
                for year in eligible_years
            )
            continue
        result = json.loads(path.read_text())["chart"]["result"][0]
        meta = result["meta"]
        currency = meta.get("currency")
        tz = meta.get("exchangeTimezoneName", "Asia/Hong_Kong")
        if currency != "HKD":
            gaps.extend(
                {**row, "year": year, "reason": "unexpected_currency_" + str(currency)}
                for year in eligible_years
            )
            continue
        q = result["indicators"]["quote"][0]
        if "close" not in q or not result.get("timestamp"):
            if tencent_output(row, eligible_years, out, events):
                continue
            gaps.extend(
                {**row, "year": year, "reason": "Yahoo empty price series"}
                for year in eligible_years
            )
            continue
        adj = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
        missing_adj = adj is None
        if missing_adj:
            adj = [np.nan] * len(result["timestamp"])
        dates = pd.to_datetime(result["timestamp"], unit="s", utc=True).tz_convert(tz).date
        prices = pd.DataFrame(
            {"date": pd.to_datetime(dates), "close": q["close"], "adjclose": adj}
        ).sort_values("date")
        dividends = []
        split_history = []
        for split in result.get("events", {}).get("splits", {}).values():
            date = pd.Timestamp(split["date"], unit="s", tz="UTC").tz_convert(tz).date()
            split_history.append(
                {"date": pd.Timestamp(date), "ratio": split["numerator"] / split["denominator"]}
            )
            splits.append(
                {
                    "ts_code": row["ts_code"],
                    "a_code": row["a_code"],
                    "date": date,
                    "numerator": split["numerator"],
                    "denominator": split["denominator"],
                    "split_ratio": split["splitRatio"],
                    "source": "Yahoo chart split event",
                }
            )
        for d in result.get("events", {}).get("dividends", {}).values():
            date = pd.Timestamp(d["date"], unit="s", tz="UTC").tz_convert(tz).date()
            dividends.append({"date": pd.Timestamp(date), "amount": d["amount"]})
            events.append(
                {
                    "ts_code": row["ts_code"],
                    "a_code": row["a_code"],
                    "date": date,
                    "amount": d["amount"],
                    "currency": currency,
                    "source": "Yahoo chart dividend event (ex-date)",
                }
            )
        em_dividends = independent_split_dividends(row["ts_code"]) if split_history else None
        if em_dividends is not None:
            events = [event for event in events if event["ts_code"] != row["ts_code"]]
        prices["return"] = prices.adjclose.pct_change(fill_method=None)
        for year in eligible_years:
            px = prices[prices.date.dt.year.eq(year)]
            valid = px[px.close.notna() & px.close.gt(0)]
            if valid.empty:
                gaps.append(
                    {**row, "year": year, "reason": "No price data / not listed during year"}
                )
                continue
            use_dividends = em_dividends if em_dividends is not None else dividends
            div = sum(d["amount"] for d in use_dividends if d["date"].year == year)
            last = valid.iloc[-1]
            rets = px["return"].dropna()
            flags = [
                "vendor_dividends_not_fully_announcement_verified",
                "ex_date_basis_excludes_pending",
                "dividend_type_not_classified",
            ]
            if missing_adj:
                flags.append("adjusted_prices_unavailable")
            if div == 0:
                flags.append("no_vendor_dividend_events_not_confirmed_zero")
            if len(rets) < 200:
                flags.append("partial_year_or_suspension")
            if result.get("events", {}).get("splits"):
                flags.append("split_events_present_verify_dividend_share_basis")
            close = last.close
            normalized_yield = None
            normalized_cash = div
            source = "Yahoo Finance chart (ex-date dividends, adjusted-price simple returns)"
            if em_dividends is not None:
                # Yahoo historical closes include future stock-split rebasing; recover actual year-end units.
                close *= np.prod([s["ratio"] for s in split_history if s["date"] > last.date])
                normalized_cash = sum(
                    d["amount"]
                    / np.prod(
                        [s["ratio"] for s in split_history if d["date"] <= s["date"] <= last.date]
                    )
                    for d in use_dividends
                    if d["date"].year == year
                )
                normalized_yield = normalized_cash / close * 100
                source = "Yahoo split-rebased prices restored to original year-end units; Eastmoney independent HKD dividend events"
                flags.append(
                    "raw_dividend_sum_varies_share_basis_in_split_year;normalized_yield_provided"
                )
                events.extend(
                    {
                        "ts_code": row["ts_code"],
                        "a_code": row["a_code"],
                        "date": d["date"].date(),
                        "amount": d["amount"],
                        "currency": "HKD",
                        "source": "Eastmoney HK F10 independent split audit",
                    }
                    for d in use_dividends
                    if d["date"].year == year
                )
            out.append(
                {
                    "year": year,
                    "ts_code": row["ts_code"],
                    "a_code": row["a_code"],
                    "name": row["name"],
                    "close": close,
                    "price_date": last.date.strftime("%Y%m%d"),
                    "cash_div": normalized_cash,
                    "yield_pct": normalized_cash / close * 100,
                    "fiscal_div": None,
                    "volatility_pct": rets.std(ddof=1) * np.sqrt(252) * 100,
                    "returns_n": len(rets),
                    "source": source,
                    "flags": ";".join(flags),
                    "currency": currency,
                    "split_normalized_yield_pct": normalized_yield,
                    "nominal_cash_div": div,
                    "nominal_yield_pct": div / close * 100,
                }
            )
    frame = pd.DataFrame(
        out,
        columns=[
            "year",
            "ts_code",
            "a_code",
            "name",
            "close",
            "price_date",
            "cash_div",
            "yield_pct",
            "fiscal_div",
            "volatility_pct",
            "returns_n",
            "source",
            "flags",
            "currency",
            "split_normalized_yield_pct",
            "nominal_cash_div",
            "nominal_yield_pct",
        ],
    )
    frame["nominal_cash_div"] = frame.nominal_cash_div.fillna(frame.cash_div)
    frame["nominal_yield_pct"] = frame.nominal_yield_pct.fillna(frame.yield_pct)
    write_csv_atomic(frame, ROOT / "h_screen_all.csv")
    write_csv_atomic(
        pd.DataFrame(gaps, columns=list(m.columns) + ["year", "reason"]),
        ROOT / "h_coverage_gaps.csv",
    )
    write_csv_atomic(
        pd.DataFrame(events, columns=["ts_code", "a_code", "date", "amount", "currency", "source"]),
        ROOT / "h_dividend_events.csv",
    )
    write_csv_atomic(
        pd.DataFrame(
            splits,
            columns=[
                "ts_code",
                "a_code",
                "date",
                "numerator",
                "denominator",
                "split_ratio",
                "source",
            ],
        ),
        ROOT / "h_split_events.csv",
    )
    print(
        "output",
        len(out),
        "stock-years;",
        len({x["ts_code"] for x in out}),
        "successful listings; gaps",
        len(gaps),
        flush=True,
    )


def independent_split_dividends(code):
    path = RAW / (code + ".eastmoney.dividends.json")
    if not path.exists():
        return None
    data = (json.loads(path.read_text()).get("result") or {}).get("data")
    if data is None:
        return None
    parsed = []
    for event in data:
        if not event.get("EX_DIVIDEND_DATE"):
            continue
        date = pd.Timestamp(event["EX_DIVIDEND_DATE"])
        if date.year not in [2023, 2024, 2025]:
            continue
        text = event.get("PLAN_EXPLAIN") or ""
        amount = re.search(r"港币\s*([\d.]+)", text)
        if amount:
            parsed.append({"date": date, "amount": float(amount.group(1)), "plan": text})
        elif "派" in text and "不分" not in text and ("人民币" in text or "港" in text):
            return None  # Never silently turn unparsed cash events into zero.
    return parsed


def supplementary_output(row, eligible_years, out, events):
    if tencent_output(row, eligible_years, out, events):
        return True
    if not args.supplementary_dividends:
        return False
    d = pd.read_csv(args.supplementary_dividends)
    d = d[d.ts_code.eq(row["ts_code"])]
    if d.empty or not d.currency.eq("HKD").all():
        return False
    try:
        raw = json.loads((RAW / (row["ts_code"] + ".eastmoney.prices.json")).read_text())["data"][
            "klines"
        ]
        adjusted = json.loads(
            (RAW / (row["ts_code"] + ".eastmoney.adjusted_prices.json")).read_text()
        )["data"]["klines"]
    except (FileNotFoundError, TypeError, KeyError):
        return False
    prices = pd.DataFrame([{"date": x.split(",")[0], "close": float(x.split(",")[2])} for x in raw])
    adj = pd.DataFrame(
        [{"date": x.split(",")[0], "adjclose": float(x.split(",")[2])} for x in adjusted]
    )
    prices = prices.merge(adj, on="date", how="left").sort_values("date")
    prices["date"] = pd.to_datetime(prices.date)
    prices["return"] = prices.adjclose.pct_change(fill_method=None)
    d["date"] = pd.to_datetime(d.date)
    for event in d.to_dict("records"):
        events.append({**event, "a_code": row["a_code"]})
    for year in eligible_years:
        px = prices[prices.date.dt.year.eq(year)]
        valid = px[px.close.notna() & px.close.gt(0)]
        if valid.empty:
            continue
        last = valid.iloc[-1]
        rets = px["return"].dropna()
        dv = d[d.date.dt.year.eq(year)].amount.sum()
        out.append(
            {
                "year": year,
                "ts_code": row["ts_code"],
                "a_code": row["a_code"],
                "name": row["name"],
                "close": last.close,
                "price_date": last.date.strftime("%Y%m%d"),
                "cash_div": dv,
                "yield_pct": dv / last.close * 100,
                "fiscal_div": None,
                "volatility_pct": rets.std(ddof=1) * np.sqrt(252) * 100,
                "returns_n": len(rets),
                "source": "Eastmoney HK daily prices; independently sourced supplementary HKD dividend events",
                "flags": "secondary_dividend_sources_crosschecked_not_officially_verified;ex_date_basis_excludes_pending;vendor_dividends_not_fully_announcement_verified",
                "currency": "HKD",
            }
        )
    return True


def tencent_output(row, eligible_years, out, events):
    code = row["ts_code"]
    rawpath = RAW / (code + ".tencent.raw.json")
    adjpath = RAW / (code + ".tencent.qfq.json")
    if not rawpath.exists() or not adjpath.exists():
        return False
    try:
        raw = json.loads(rawpath.read_text())["data"]["hk" + code[:5]]["day"]
        adj = json.loads(adjpath.read_text())["data"]["hk" + code[:5]]["qfqday"]
    except (KeyError, TypeError):
        return False
    if args.supplementary_dividends:
        d = pd.read_csv(args.supplementary_dividends)
        d = d[d.ts_code.eq(code)].to_dict("records")
    else:
        d = []
    if not d:
        d = independent_split_dividends(code)
        if d is None:
            return False
    prices = pd.DataFrame([{"date": x[0], "close": float(x[2])} for x in raw])
    adjusted = pd.DataFrame([{"date": x[0], "adjclose": float(x[2])} for x in adj])
    prices = prices.merge(adjusted, on="date", how="left").sort_values("date")
    prices["date"] = pd.to_datetime(prices.date)
    prices["return"] = prices.adjclose.pct_change(fill_method=None)
    events.extend(
        {
            "ts_code": code,
            "a_code": row["a_code"],
            "date": str(event["date"]),
            "amount": event["amount"],
            "currency": "HKD",
            "source": event.get("source", "Eastmoney HK dividend event"),
        }
        for event in d
    )
    for year in eligible_years:
        px = prices[prices.date.dt.year.eq(year)]
        valid = px[px.close.notna() & px.close.gt(0)]
        if valid.empty:
            continue
        last = valid.iloc[-1]
        rets = px["return"].dropna()
        dv = sum(event["amount"] for event in d if pd.Timestamp(event["date"]).year == year)
        flags = [
            "vendor_dividends_not_fully_announcement_verified",
            "ex_date_basis_excludes_pending",
        ]
        if not d:
            flags.append("no_vendor_dividend_events_not_confirmed_zero")
        if len(rets) < 200:
            flags.append("partial_year_or_suspension")
        out.append(
            {
                "year": year,
                "ts_code": code,
                "a_code": row["a_code"],
                "name": row["name"],
                "close": last.close,
                "price_date": last.date.strftime("%Y%m%d"),
                "cash_div": dv,
                "yield_pct": dv / last.close * 100,
                "fiscal_div": None,
                "volatility_pct": rets.std(ddof=1) * np.sqrt(252) * 100,
                "returns_n": len(rets),
                "source": "Tencent original daily price and qfq returns; independent HKD dividend events",
                "flags": ";".join(flags),
                "currency": "HKD",
            }
        )
    return True


if __name__ == "__main__":
    m = mapping()
    if args.mode == "probe":
        print(chart({"ts_code": "06030.HK"}), flush=True)
    elif args.mode == "fallback":
        fallback()
    elif args.mode == "audit":
        codes = (
            pd.read_csv(ROOT / "h_split_events.csv")
            .ts_code.str.replace(".HK", "", regex=False)
            .drop_duplicates()
            .tolist()
        )
        codes += ["00638", "00699", "01839"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda code: fallback([code]), codes))
    elif args.mode == "tencent":
        for code in ["01839", "00638", "00699"]:
            for adjust in ["", "qfq"]:
                try:
                    url = (
                        "https://web.ifzq.gtimg.cn/appstock/app/"
                        + ("hkfqkline" if adjust else "fqkline")
                        + "/get"
                    )
                    parameter = f"hk{code},day,2022-12-30,2025-12-31,1000," + adjust
                    resp = requests.get(url, params={"param": parameter}, timeout=20)
                    obj = resp.json()
                    (RAW / (code + ".HK.tencent." + (adjust or "raw") + ".json")).write_text(
                        json.dumps(obj)
                    )
                    print(code, adjust, str(obj)[:300], flush=True)
                except Exception as error:
                    print(code, adjust, str(error)[:150], flush=True)
    elif args.mode == "fetch":
        eligible = m[m.h_list_date.le("20251231")]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for i, result in enumerate(pool.map(chart, eligible.to_dict("records"))):
                print(i + 1, result, flush=True)
        output(m)
    else:
        output(m)
