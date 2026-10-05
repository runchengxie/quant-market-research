"""Export a source-labelled annual screen workbook from an external acquisition run."""

import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from market_research.dividend_screen import normalize_tushare_cash, payout_ratios


def fiscal_history(root, as_of):
    d = pd.read_parquet(root / "selected_dividend_history.parquet")
    d = d[d.div_proc.eq("实施") & d.ex_date.notna() & d.ex_date.le(as_of)].copy()
    d = d[d.end_date.str[:4].isin(["2023", "2024", "2025"])]
    d["cash_div_tax"] = pd.to_numeric(d.cash_div_tax, errors="coerce")
    d.loc[d.ts_code.eq("689009.SH"), "cash_div_tax"] /= 10
    overrides = pd.read_csv(root / "reviewed_event_overrides.csv", dtype=str)
    for o in overrides.to_dict("records"):
        mask = (
            d.ts_code.eq(o["ts_code"]) & d.ex_date.eq(o["ex_date"]) & d.end_date.eq(o["end_date"])
        )
        d.loc[mask, "cash_div_tax"] = float(o["cash_div_tax"])
    d = d[d.cash_div_tax.ge(0)].copy()
    keys = ["ts_code", "end_date", "ex_date"]
    c = d.groupby(keys).cash_div_tax.nunique()
    if c.gt(1).any():
        bad = d.merge(c[c.gt(1)].reset_index()[keys], on=keys)
        bad.to_csv(root / "fiscal_conflicts.csv", index=False)
        raise ValueError("unreviewed fiscal dividend conflicts")
    d = d.sort_values("ann_date").drop_duplicates(keys, keep="last")
    d = normalize_tushare_cash(d)
    # Differential holder-class rates cannot be multiplied by all shares.
    d.loc[d.ts_code.eq("600989.SH"), "cash_amount"] = np.nan
    d["year"] = d.end_date.str[:4].astype(int)
    g = d.groupby(["ts_code", "year"])
    totals = g.agg(
        fiscal_dps=("cash_div_tax", "sum"),
        fiscal_cash_amount=("cash_amount", lambda s: s.sum() if s.notna().all() else np.nan),
        fiscal_events=("cash_div_tax", "size"),
        fiscal_last_ex_date=("ex_date", "max"),
    ).reset_index()
    d.to_csv(root / "fiscal_dividend_events.csv", index=False, encoding="utf-8-sig")
    return totals


def make_tables(root, source, as_of):
    a = pd.read_parquet(root / "a_all_years_base.parquet")
    v = pd.read_parquet(root / "a_volatility.parquet")
    a = a.merge(v, on=["ts_code", "year"], how="left", validate="one_to_one")
    a["source"] = "Tushare dividend/daily/daily_basic/adj_factor + local normalized financials"
    a["currency"] = "CNY"
    a["flags"] = ""
    nc = pd.read_parquet(source / "namechange/a_share_all_namechange_latest.parquet")
    a["name_current"] = a.name
    for year in [2023, 2024, 2025]:
        x = nc[
            nc.start_date.le(str(year) + "1231")
            & (nc.end_date.isna() | nc.end_date.ge(str(year) + "1231"))
        ]
        names = (
            x.sort_values("start_date")
            .drop_duplicates("ts_code", keep="last")
            .set_index("ts_code")
            .name
        )
        mask = a.year.eq(year)
        a.loc[mask, "name"] = a.loc[mask, "ts_code"].map(names).fillna(a.loc[mask, "name"])
    a = a.merge(
        fiscal_history(root, as_of), on=["ts_code", "year"], how="left", validate="one_to_one"
    )
    a["fiscal_yield_pct"] = a.fiscal_dps / a.close * 100
    a["nominal_yield_pct"] = a.nominal_cash_div / a.close * 100
    a["fiscal_cash_cny_billion"] = a.fiscal_cash_amount / 1e8
    a["net_profit_parent"] = a.n_income_attr_p
    a["cash_amount"] = a.fiscal_cash_amount
    a["cash_div_tax"] = a.fiscal_dps
    a = payout_ratios(a)
    a["payout_method"] = a.payout_method.replace(
        {
            "cash_amount/net_profit_parent": "供应商基准股本推算现金总额/归母净利",
            "dps/eps_proxy": "每股分红/EPS代理",
            "unavailable": "缺失",
        }
    )
    for condition, flag in [
        (a.stock_div.gt(0), "同年送转已折算到年末份额"),
        (a.returns_n.lt(200), "波动率样本不足200日"),
        (a.price_stale_days.gt(10), "年末停牌或报价陈旧"),
        (a.missing_adj.gt(0), "复权因子缺失"),
        (a.net_profit_parent.le(0), "财年亏损，派息率不适用"),
        (a.payout_pct.gt(100), "财年派息率超过100%，需检查特殊分红及口径"),
    ]:
        a.loc[condition, "flags"] += flag + ";"
    h = pd.read_csv(
        root / "h_screen_all.csv", dtype={"ts_code": str, "a_code": str, "price_date": str}
    )
    issuer_cols = [
        "a_code",
        "year",
        "industry",
        "is_broker",
        "industry_name",
        "head_proxy",
        "industry_mv_rank",
        "industry_members",
        "revenue_cny",
        "n_income_attr_p",
        "total_assets",
        "total_liab",
        "total_hldr_eqy_exc_min_int",
        "roe",
        "roe_waa",
        "roa",
        "debt_to_assets",
        "netprofit_yoy",
        "tr_yoy",
        "n_cashflow_act",
        "eps",
        "bps",
        "payout_pct",
        "payout_method",
        "fiscal_cash_cny_billion",
        "income_ann_date",
        "balancesheet_ann_date",
        "cashflow_ann_date",
        "fina_indicator_ann_date",
    ]
    h = h.merge(a[issuer_cols], on=["a_code", "year"], how="left", validate="many_to_one")
    h["name_current"] = h.name
    h.loc[h.ts_code.eq("02611.HK") & h.year.le(2024), "name"] = "国泰君安（现国泰海通）"
    h["market"] = "H"
    h["trade_date"] = h.price_date
    if "nominal_cash_div" not in h:
        h["nominal_cash_div"] = np.nan
    h["fiscal_dps"] = np.nan
    h["fiscal_yield_pct"] = np.nan
    if "nominal_yield_pct" not in h:
        h["nominal_yield_pct"] = np.nan
    h["price_stale_days"] = (
        pd.to_datetime(h.year.astype(str) + "1231") - pd.to_datetime(h.price_date)
    ).dt.days
    # H issuer financials use the same consolidated annual statements. H valuations
    # and H fiscal DPS are missing; A valuations/DPS must never be copied to H rows.
    allrows = pd.concat([a, h], ignore_index=True)
    allrows["selected"] = allrows.yield_pct.gt(5)
    for original, target in [
        ("revenue_cny", "revenue_100m"),
        ("n_income_attr_p", "profit_100m"),
        ("total_assets", "assets_100m"),
        ("total_hldr_eqy_exc_min_int", "equity_100m"),
        ("n_cashflow_act", "ocf_100m"),
    ]:
        allrows[target] = allrows[original] / 1e8
    allrows["market_cap_100m"] = allrows.total_mv / 1e4
    allrows["ocf_profit_ratio"] = allrows.n_cashflow_act / allrows.n_income_attr_p.where(
        allrows.n_income_attr_p.ne(0)
    )
    allrows["dv_ttm_diff_pp"] = allrows.yield_pct - allrows.dv_ttm
    selected = allrows[allrows.selected].sort_values(
        ["year", "market", "yield_pct"], ascending=[True, True, False]
    )
    brokers = (
        allrows[allrows.is_broker.eq(True)]
        .sort_values(["year", "yield_pct"], ascending=[True, False])
        .copy()
    )
    selected.to_csv(root / "selected_all.csv", index=False, encoding="utf-8-sig")
    brokers.to_csv(root / "brokers_all.csv", index=False, encoding="utf-8-sig")
    allrows.to_parquet(root / "all_years_final.parquet", index=False)
    return allrows, selected, brokers


COLS = {
    "year": "年度",
    "market": "市场",
    "ts_code": "证券代码",
    "a_code": "对应A股代码",
    "name": "名称",
    "name_current": "当前名称",
    "industry_name": "申万一级行业（当年）",
    "industry": "Tushare细分行业（当前）",
    "head_proxy": "头部代理标记",
    "industry_mv_rank": "行业年末市值排名",
    "industry_members": "行业A股公司数",
    "cash_div": "实施股息_每年末份额",
    "currency": "价格与股息币种",
    "nominal_cash_div": "原始每股股息合计",
    "close": "年末未复权收盘价",
    "trade_date": "价格日期",
    "yield_pct": "主口径股息率_%",
    "nominal_yield_pct": "未折算送转股息率_%",
    "dv_ratio": "Tushare_dv_ratio_%",
    "dv_ttm": "Tushare_dv_ttm_%",
    "dv_ttm_diff_pp": "主口径与dv_ttm差_百分点",
    "fiscal_dps": "所属财年每股分红_原始人民币",
    "fiscal_yield_pct": "财年分红对照股息率_%",
    "fiscal_cash_cny_billion": "所属财年现金分红_亿元_基准股本推算",
    "payout_pct": "公司财年派息率_%",
    "payout_method": "派息率计算方法",
    "volatility_pct": "年化波动率_%",
    "returns_n": "波动率有效收益日数",
    "market_cap_100m": "A报价总市值_亿元",
    "pe": "年末A股PE",
    "pe_ttm": "年末A股PE_TTM",
    "pb": "年末A股PB",
    "revenue_100m": "年度营业收入_亿元",
    "profit_100m": "年度归母净利润_亿元",
    "netprofit_yoy": "归母净利润同比_%",
    "tr_yoy": "营业收入同比_%",
    "roe": "ROE_%",
    "roe_waa": "加权ROE_%",
    "roa": "ROA_%",
    "eps": "公司年度EPS_人民币",
    "bps": "每股净资产_人民币",
    "assets_100m": "总资产_亿元",
    "equity_100m": "归母净资产_亿元",
    "debt_to_assets": "资产负债率_%",
    "ocf_100m": "经营现金流净额_亿元",
    "ocf_profit_ratio": "经营现金流_归母净利比",
    "price_stale_days": "价格距年底天数",
    "income_ann_date": "利润表披露日期",
    "flags": "数据与解释标记",
    "source": "来源",
}


def display(df):
    df = df.copy()
    if "flags" in df:
        translations = {
            "vendor_dividends_not_fully_announcement_verified": "供应商股息记录，未逐条核对公告",
            "ex_date_basis_excludes_pending": "按除息年计算，不计尚未实施方案",
            "dividend_type_not_classified": "普通与特别股息未完全区分",
            "partial_year_or_suspension": "上市不足一年或停牌，波动率样本较短",
            "secondary_dividend_sources_crosschecked_not_officially_verified": "股息经多个公开来源交叉核对，未逐条核对官方公告",
            "no_vendor_dividend_events_not_confirmed_zero": "供应商无股息事件，未逐公告确认零分红",
            "split_events_present_verify_dividend_share_basis": "发生送股或拆股，股息份额另经核对",
            "raw_dividend_sum_varies_share_basis_in_split_year": "原始分红份额在年内变化",
            "normalized_yield_provided": "主股息率已统一至年末份额",
        }
        for key, text in translations.items():
            df["flags"] = df["flags"].fillna("").str.replace(key, text, regex=False)
    return df.reindex(columns=COLS).rename(columns=COLS)


def export(root, source, as_of):
    allrows, selected, brokers = make_tables(root, source, as_of)
    summary = (
        allrows.groupby(["year", "market"])
        .agg(universe=("ts_code", "size"), selected=("selected", "sum"))
        .reset_index()
    )
    notes = [
        (
            "主口径",
            "2023、2024、2025分别筛选，税前实施现金股息按除息日归年/该年末最后可得收盘价，严格>5%。属于回顾性筛选。",
        ),
        (
            "送转口径",
            "A每笔现金分红折算到同年末送转后份额；同时列原始合计。仅修正送转，不把新股增发当拆股。CDR九号公司分红单位按公告由每10份改为每份。",
        ),
        (
            "财年对照",
            "分红所属财年另列，含截至获取日后来实施的分红，可能2026实施2025年报分红；不能用作2025年底已知信息。",
        ),
        (
            "头部",
            "可复算代理：申万一级行业年末A报价总市值前三；证券细分单独排名。非竞争地位/盈利质量认定。H沿用同发行人A排名，不重复计入。",
        ),
        (
            "市值",
            "Tushare total_mv按A股价乘总股本，A+H不等于A与H市值相加；仅作统一排名代理。未补H的PE/PB/财年每股港元股息。",
        ),
        (
            "波动率",
            "复权日简单收益率样本标准差×sqrt(252)×100，含前一年末价计算首日收益，不填充缺失。不足200日保留值并标记。",
        ),
        (
            "财务",
            "各年度合并报表，采用截至本次获取日可得的更新版本，原始Tushare财务资产；H使用同发行人A合并财务，单位亿元人民币。不是历史PIT快照。",
        ),
        (
            "派息率",
            "优先Tushare基准股本×每股分红得到总现金/年度归母净利润；基准不全则EPS代理且标明。差异化股东分红不外推总额。",
        ),
        (
            "H来源",
            "Yahoo实际除息事件与港币价格、复权价；补充来源逐行注明。全量未逐条核对公告；特殊股息未完全分类。H事件不复制A股分红。",
        ),
        (
            "H覆盖",
            "同一法律发行人精确匹配A/H、每年末均仍上市。匹配的覆盖范围与未取得的股年见H映射和H缺口。",
        ),
        (
            "无分红",
            "A主事件逐日查询全日历1096天且无失败；0表示完整事件范围内未发现现金分红。H依赖供应商事件覆盖，不能把0视为公告证明。",
        ),
        (
            "注意",
            "一次性/特别分红、亏损、上市不足一年、停牌与送转等可影响可持续性；股票分红历史不保证未来分红。金融业经营现金流不与制造业简单比较。",
        ),
        ("数据截至", as_of),
    ]
    guosen = pd.DataFrame(
        [
            {
                "口径": "Tushare dv_ttm / 实施TTM",
                "分红元每股": 0.45,
                "股价": 9.8,
                "股息率_%": 0.45 / 9.8 * 100,
                "状态": "2026-02-11 0.10 + 2026-06-22 0.35，官方实施公告支持",
            },
            {
                "口径": "通达信5.61%反推",
                "分红元每股": 0.55,
                "股价": 9.8,
                "股息率_%": 0.55 / 9.8 * 100,
                "状态": "同价差0.10。2026中期0.10方案截至Tushare查询为股东大会通过，未见实施；通达信是否计入待核实",
            },
            {
                "口径": "Tushare dv_ratio",
                "分红元每股": np.nan,
                "股价": 9.8,
                "股息率_%": 3.352,
                "状态": "2026-09-30原始接口值，不能当实施TTM",
            },
        ]
    )
    workbook = root / "dividend_screen_2023_2025.xlsx"
    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        pd.DataFrame(notes, columns=["项目", "说明"]).to_excel(
            writer, sheet_name="说明", index=False
        )
        summary.rename(
            columns={
                "year": "年度",
                "market": "市场",
                "universe": "有数据年度证券数",
                "selected": "股息率超过5%",
            }
        ).to_excel(writer, sheet_name="汇总", index=False)
        for year in [2023, 2024, 2025]:
            display(selected[selected.year.eq(year)]).to_excel(
                writer, sheet_name=f"{year}_入选", index=False
            )
        display(brokers[brokers.selected]).to_excel(writer, sheet_name="券商_入选", index=False)
        display(brokers).to_excel(writer, sheet_name="券商_全部对照", index=False)
        counts = selected.groupby("ts_code").year.nunique()
        display(selected[selected.ts_code.isin(counts[counts.eq(3)].index)]).to_excel(
            writer, sheet_name="连续三年", index=False
        )
        guosen.to_excel(writer, sheet_name="国信证券_口径", index=False)
        display(allrows[allrows.ts_code.eq("002736.SZ")]).to_excel(
            writer, sheet_name="国信证券_年度", index=False
        )
        for file, sheet in [
            ("dividend_events.csv", "A_分红事件"),
            ("h_dividend_events.csv", "H_分红事件"),
            ("ah_mapping.csv", "AH映射"),
            ("h_coverage_gaps.csv", "H缺口"),
            ("reviewed_event_overrides.csv", "核实修正"),
        ]:
            pd.read_csv(root / file).to_excel(writer, sheet_name=sheet, index=False)
        display(allrows[allrows.market.eq("A")]).to_excel(
            writer, sheet_name="A_全市场年末", index=False
        )
        for ws in writer.book.worksheets:
            ws.freeze_panes = "F2" if ws.max_column > 8 else "A2"
            ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                cell.fill = PatternFill("solid", fgColor="193B4F")
                cell.font = Font(color="FFFFFF", bold=True)
                cell.alignment = Alignment(wrap_text=True, vertical="center")
            ws.row_dimensions[1].height = 40
            for col in ws.columns:
                title = str(col[0].value)
                width = 22 if len(title) > 12 else 17
                if title in ["来源", "数据与解释标记", "说明", "状态"]:
                    width = 65
                ws.column_dimensions[col[0].column_letter].width = width
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    if isinstance(cell.value, float):
                        cell.number_format = "0.0000"
    links = {
        "Tushare股息字段": "https://tushare.pro/document/2?doc_id=32",
        "Tushare分红字段": "https://tushare.pro/document/2?doc_id=103",
        "国信前三季度实施": "https://disc.static.szse.cn/disc/disk03/finalpage/2026-02-04/e94ca57a-f63b-4178-9423-39fb6d62a83a.PDF",
        "国信年度实施": "https://disc.static.szse.cn/disc/disk03/finalpage/2026-06-13/2c4d8266-25cd-4773-a331-4c948f78aa0d.PDF",
    }
    detailcols = [
        "year",
        "market",
        "ts_code",
        "name",
        "yield_pct",
        "cash_div",
        "close",
        "volatility_pct",
        "industry_name",
        "head_proxy",
        "flags",
    ]
    btable = (
        display(brokers[brokers.selected])[[COLS[c] for c in detailcols]]
        .round(4)
        .to_html(index=False, na_rep="缺失")
    )
    rows = []
    for year in [2023, 2024, 2025]:
        y = selected[selected.year.eq(year)]
        rows.append(
            f"<section><h2>{year} 年入选名单</h2><p>A 股 {sum(y.market.eq('A'))}，H 股 {sum(y.market.eq('H'))}。点击 Excel 查看全部财务与口径对照。</p>{display(y)[[COLS[c] for c in detailcols]].round(4).to_html(index=False, na_rep='缺失')}</section>"
        )
    gap = pd.read_csv(root / "h_coverage_gaps.csv")
    sources = " ".join(f'<a href="{u}">{n}</a>' for n, u in links.items())
    notes_html = "".join(f"<p><strong>{n}：</strong>{v}</p>" for n, v in notes)
    html = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2023—2025 股息率筛选</title><style>body{{font:16px/1.6 system-ui;margin:auto;padding:32px;max-width:1500px;color:#18333c;background:#f8fafb}}h1,h2{{color:#193b4f}}section{{background:white;padding:24px;margin:24px 0;border-radius:12px;overflow:auto}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{padding:9px;border-bottom:1px solid #dae4e8;text-align:left}}th{{background:#e5eef2;white-space:normal}}td:nth-child(3),th:nth-child(3){{min-width:85px}}td:nth-child(4),th:nth-child(4){{min-width:160px}}td:last-child{{max-width:360px;overflow-wrap:anywhere}}a{{color:#006f7c}}strong{{color:#203e49}}.warning{{padding:16px;background:#fff4dc;border-left:4px solid #c99932}}details{{background:#fff;padding:20px}}p{{max-width:1000px}}</style><h1>2023—2025：年度股息率超过 5%</h1><p>按实施除息年独立计算；税前股息与年末价格使用同一份额口径。数据截至 {as_of}。</p><p><a href="{workbook.name}">下载完整 Excel：年度名单、财务、波动率、行业与头部标记</a></p><section><h2>年度结果</h2>{summary.rename(columns={"year": "年度", "market": "市场", "universe": "有数据证券数", "selected": "入选数"}).to_html(index=False)}<p class="warning">已匹配 H 股样本的价格缺口为 {len(gap)} 个股年。含送转、停牌、短样本及供应商未逐条公告核实等标记，不能把筛选结果视为持续分红保证。</p>{gap.to_html(index=False, na_rep="—") if len(gap) else "<p>已匹配历史样本的价格齐全；法律主体更名可能造成映射遗漏，覆盖范围与来源见 Excel。</p>"}</section><section><h2>券商行业入选</h2>{btable}<p>A 股券商在主口径下三年均无股息率超过 5% 的标的。Excel 同时列出券商全行业对照，可切换查看 dv_ratio 等口径。</p></section><section><h2>国信证券：4.59% 与 5.61%</h2><p>已实施每股 0.10 + 0.35 = 0.45 元；除以 2026-09-30 收盘价 9.80 元，股息率为 4.5918%。同价下 5.61% 相当于每股 0.55 元。另有 0.10 元中期方案尚未见实施，能解释金额差但未取得通达信算法说明，因此原因仍属待核实推断。</p>{guosen.to_html(index=False)}<p>{sources}</p></section>{"".join(rows)}<details><summary>计算口径、来源与限制</summary>{notes_html}</details></html>'''
    (root / "report.html").write_text(html, encoding="utf-8")
    files = ["selected_all.csv", "brokers_all.csv", "dividend_screen_2023_2025.xlsx", "report.html"]
    manifest = {
        "schema_version": "dividend-screen.v1",
        "as_of": as_of,
        "years": [2023, 2024, 2025],
        "summary": summary.to_dict("records"),
        "h_gaps": gap.to_dict("records"),
        "artifact_hashes": {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files
        },
        "method": "implemented ex-date cash dividends restated for same-year stock distributions / final unadjusted close; >5%; annual simple adjusted return sd sqrt252",
        "limitations": dict(notes),
    }
    repo = Path(__file__).resolve().parents[1]

    def checksum(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    code_paths = [
        Path(__file__),
        repo / "scripts/research_dividend_screen.py",
        repo / "scripts/hk_dividend_fetch.py",
        repo / "src/market_research/dividend_screen.py",
        repo / "uv.lock",
    ]
    manifest["code_hashes"] = {str(p.relative_to(repo)): checksum(p) for p in code_paths}
    manifest["code_git_commit"] = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    manifest["code_dirty"] = bool(
        subprocess.check_output(
            ["git", "-C", str(repo), "status", "--porcelain"], text=True
        ).strip()
    )
    inputs = [
        "implemented_dividends_2023_2025.parquet",
        "selected_dividend_history.parquet",
        "a_volatility.parquet",
        "annual_financials.parquet",
        "a_all_years_base.parquet",
        "h_screen_all.csv",
        "ah_mapping.csv",
        "h_dividend_events.csv",
        "h_split_events.csv",
        "h_supplementary_dividends.csv",
        "reference/hk_basic_listed.parquet",
        "reference/hk_basic_delisted.parquet",
    ]
    manifest["run_input_hashes"] = {
        name: checksum(root / name) for name in inputs if (root / name).exists()
    }
    asset_names = [
        "daily/a_share_all_daily_latest",
        "daily_basic/a_share_all_daily_basic_latest",
        "adj_factor/a_share_all_adj_factor_latest",
        "normalized_fundamentals/a_share_all_normalized_fundamentals_latest",
        "sw_industry_member/a_share_all_sw_industry_member_latest",
    ]
    manifest["shared_snapshot_paths"] = {
        name: str((source / name).resolve()) for name in asset_names
    }
    manifest["shared_asset_manifests"] = {
        name: {
            "path": str((source / name / "manifest.yml").resolve()),
            "sha256": checksum(source / name / "manifest.yml"),
            "content": (source / name / "manifest.yml").read_text(),
        }
        for name in asset_names
        if (source / name / "manifest.yml").exists()
    }
    source_files = [
        source / "instruments/a_share_all_instruments_latest.parquet",
        source / "namechange/a_share_all_namechange_latest.parquet",
        source / "sw_industry_member/a_share_all_sw_industry_member_latest/data/part.parquet",
    ]
    source_files += list(
        (
            source / "normalized_fundamentals/a_share_all_normalized_fundamentals_latest/components"
        ).glob("*/data/part.parquet")
    )
    source_files += [
        source / f"daily_basic/a_share_all_daily_basic_latest/data/trade_date={date}/part.parquet"
        for date in ["20231229", "20241231", "20251231"]
    ]
    manifest["shared_input_hashes"] = {
        str(p.resolve()): checksum(p) for p in source_files if p.exists()
    }
    manifest["runtime"] = {
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print(summary.to_string(index=False))
    print("Broker selected:\n" + brokers[brokers.selected][detailcols].to_string(index=False))
    print("Output:", workbook)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--as-of", default="20261005")
    args = parser.parse_args()
    export(args.output_dir, args.source_root, args.as_of)
