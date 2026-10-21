#!/usr/bin/env python3
"""Read-only terminal inventory analysis of a frozen adjusted-unit ledger.

No portfolio rerun, transaction, recovery assumption or alteration of source cash
and units. Outputs are private external research artifacts, never public inputs.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from math import isclose, isfinite
from pathlib import Path


RATES = (0.0, 0.5, 1.0)
CLASSES = ("terminal_unsettled", "missing_terminal_quote", "valued_exit_blocked")


def number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if isfinite(result) else None


def positive(value):
    result = number(value)
    return result if result is not None and result > 0 else None


def close(a, b):
    return isclose(a, b, rel_tol=1e-10, abs_tol=1e-7)


def terminal_analysis(
    portfolio, holdings, anchors, last_attempts, sessions, initial_capital=1_000_000.0
):
    """Analyze one full terminal inventory with independently derived anchors.

    ``anchors`` must come from the latest positive finite historical
    observed_adjusted_close ledger mark per lot, not arbitrary vendor quotes.
    ``sessions`` is the persisted daily ledger calendar, not weekdays.
    """
    if not positive(initial_capital):
        raise ValueError("positive initial capital required")
    if not sessions or sessions != sorted(set(sessions)):
        raise ValueError("persisted daily calendar must be sorted and unique")
    end = portfolio["last_date"]
    if end != sessions[-1] or portfolio["final"]["date"] != end:
        raise ValueError("terminal date differs from persisted calendar")
    final = portfolio["final"]
    cash = number(final["cash"])
    if cash is None or cash < -1e-7:
        raise ValueError("invalid scenario cash")
    ids = [h["lot_id"] for h in holdings]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate terminal lot")
    rows = []
    for h in holdings:
        if h["date"] != end:
            raise ValueError("nonterminal holding passed to analysis")
        units = positive(h["units"])
        if units is None:
            raise ValueError("invalid held units")
        source = h["mark_source"]
        price = positive(h.get("mark_price"))
        if source == "observed_adjusted_close" and price is not None:
            valuation_class = "valued_exit_blocked"
            current_value = units * price
            if number(h.get("marked_value")) is None or not close(current_value, h["marked_value"]):
                raise ValueError("current mark identity differs")
        elif source in {"unresolved_terminal", "unresolved_missing_quote"} and price is None:
            valuation_class = (
                "terminal_unsettled"
                if source == "unresolved_terminal"
                else "missing_terminal_quote"
            )
            current_value = None
            if number(h.get("marked_value")) is not None:
                raise ValueError("unpriced inventory unexpectedly has a marked value")
        else:
            raise ValueError("unknown or inconsistent terminal valuation source")
        anchor = anchors.get(h["lot_id"], {})
        anchor_price = positive(anchor.get("price"))
        anchor_date = anchor.get("date") if anchor_price is not None else None
        if anchor_date:
            if anchor_date not in sessions or anchor_date > end:
                raise ValueError("anchor is future-dated or outside persisted sessions")
            age_sessions = bisect_right(sessions, end) - bisect_right(sessions, anchor_date)
            age_calendar = (
                datetime.strptime(end, "%Y%m%d") - datetime.strptime(anchor_date, "%Y%m%d")
            ).days
        else:
            age_sessions = age_calendar = None
        retained_price = positive(h.get("last_observed_price"))
        retained_date = h.get("last_observed_date")
        anchor_matches_retained = (
            anchor_price is not None
            and retained_price is not None
            and close(anchor_price, retained_price)
            and anchor_date == retained_date
        )
        if anchor_price is not None and not anchor_matches_retained:
            raise ValueError("historical mark anchor disagrees with retained last-observed fields")
        if current_value is not None and (anchor_date != end or not anchor_matches_retained):
            raise ValueError("current valued lot lacks matching current historical mark")
        reference_value = (
            current_value
            if current_value is not None
            else units * anchor_price
            if anchor_price is not None
            else None
        )
        if reference_value is not None and not isfinite(reference_value):
            raise ValueError("nonfinite reference value")
        attempt = last_attempts.get(h["lot_id"], {})
        attempt_date = attempt.get("date")
        if attempt_date and attempt_date > end:
            raise ValueError("future exit attempt")
        if attempt.get("status") == "filled":
            raise ValueError("terminal lot has a filled final exit")
        rows.append(
            dict(
                portfolio=portfolio["portfolio"],
                metric=portfolio["metric"],
                quintile=portfolio["quintile"],
                scenario=portfolio["scenario"],
                terminal_date=end,
                lot_id=h["lot_id"],
                symbol=h["symbol"],
                cohort=h["cohort"],
                units=units,
                exit_requested_date=h.get("requested_date"),
                valuation_class=valuation_class,
                terminal_mark_source=source,
                current_mark_price=price,
                current_marked_value=current_value,
                last_valid_price=anchor_price,
                last_valid_date=anchor_date,
                last_quote_age_sessions=age_sessions,
                last_quote_age_calendar_days=age_calendar,
                anchor_status="eligible_ledger_history"
                if anchor_price is not None
                else "no_eligible_historical_mark",
                anchor_matches_retained=anchor_matches_retained,
                retained_last_observed_price=retained_price,
                retained_last_observed_date=retained_date,
                reference_value=reference_value,
                reference_weight_initial=reference_value / initial_capital
                if reference_value is not None
                else None,
                last_exit_attempt_date=attempt_date,
                last_exit_status=attempt.get("status", "no_exit_attempt_record"),
                last_exit_reason=attempt.get("reason"),
                final_session_exit_attempt=attempt_date == end,
            )
        )
    current = sum(r["current_marked_value"] or 0.0 for r in rows)
    unpriced = [r for r in rows if r["current_marked_value"] is None]
    unknown = sum(r["reference_value"] is None for r in unpriced)
    last_value = sum(r["reference_value"] or 0.0 for r in unpriced)
    reference_known_component = cash + current + last_value
    reference_total = None if unknown else reference_known_component
    for r in rows:
        r["reference_weight_total"] = (
            r["reference_value"] / reference_total
            if r["reference_value"] is not None and reference_total and reference_total > 0
            else None
        )
    if len(rows) != final["holding_lots"] or len(unpriced) != final["unresolved_lots"]:
        raise ValueError("terminal inventory count differs from frozen summary")
    if sum(bool(r["exit_requested_date"]) for r in rows) != final["pending_exit_lots"]:
        raise ValueError("pending exit count differs from frozen summary")
    if not close(current, final["known_marked_value"]) or not close(
        cash + current, final["zero_unresolved_nav"]
    ):
        raise ValueError("terminal mark or zero-unresolved identity differs")
    scenarios = []
    for scope in ("A_unpriced_only", "B_all_remaining"):
        base = cash + current if scope == "A_unpriced_only" else cash
        reference = last_value if scope == "A_unpriced_only" else current + last_value
        for rate in RATES:
            component = base + rate * reference
            # Zero is an explicit full-impairment assumption, including unknown
            # anchors; unknown counts remain visible. Other rates remain unknown.
            value = component if not unknown or rate == 0 else None
            scenarios.append(
                dict(
                    portfolio=portfolio["portfolio"],
                    metric=portfolio["metric"],
                    quintile=portfolio["quintile"],
                    scenario=portfolio["scenario"],
                    scope=scope,
                    reference_fraction=rate,
                    cash=cash,
                    current_marked_value=current,
                    known_unpriced_reference=last_value,
                    unknown_reference_lots=unknown,
                    reference_complete=unknown == 0,
                    reference_total_value=reference_total,
                    reference_total_known_component=reference_known_component,
                    scenario_value=value,
                    scenario_known_component=component,
                    scenario_change_from_initial=value / initial_capital - 1
                    if value is not None
                    else None,
                    valuation_only=True,
                    cash_change=0.0,
                    units_changed=False,
                    not_recovery_probability_or_bound=True,
                )
            )
    groups = defaultdict(list)
    for r in rows:
        groups[(r["valuation_class"], r["last_exit_status"], r["last_exit_reason"])].append(r)
    reasons = []
    for (kind, status, reason), group in sorted(groups.items(), key=lambda pair: str(pair[0])):
        values = [r["reference_value"] for r in group if r["reference_value"] is not None]
        ages = [
            r["last_quote_age_sessions"] for r in group if r["last_quote_age_sessions"] is not None
        ]
        unknown_n = len(group) - len(values)
        value = None if unknown_n else sum(values)
        reasons.append(
            dict(
                portfolio=portfolio["portfolio"],
                metric=portfolio["metric"],
                quintile=portfolio["quintile"],
                scenario=portfolio["scenario"],
                valuation_class=kind,
                last_exit_status=status,
                last_exit_reason=reason,
                lots=len(group),
                unknown_reference_lots=unknown_n,
                reference_value=value,
                reference_known_component=sum(values),
                reference_weight_initial=value / initial_capital if value is not None else None,
                reference_weight_total=value / reference_total
                if value is not None and reference_total and reference_total > 0
                else None,
                max_last_quote_age_sessions=max(ages) if ages else None,
                unknown_quote_age_lots=len(group) - len(ages),
            )
        )
    summary = dict(
        portfolio=portfolio["portfolio"],
        metric=portfolio["metric"],
        quintile=portfolio["quintile"],
        scenario=portfolio["scenario"],
        terminal_date=end,
        initial_capital=initial_capital,
        cash=cash,
        holding_lots=len(rows),
        unpriced_lots=len(unpriced),
        valued_but_unexited_lots=len(rows) - len(unpriced),
        fully_liquidated=len(rows) == 0,
        strict_terminal_value_available=final["strict_nav"] is not None,
        current_marked_value=current,
        known_unpriced_reference=last_value,
        unknown_reference_lots=unknown,
        reference_total_value=reference_total,
        reference_complete=unknown == 0,
        reference_total_known_component=reference_known_component,
        unpriced_reference_weight_initial=last_value / initial_capital if not unknown else None,
        unpriced_reference_weight_total=last_value / reference_total
        if not unknown and reference_total and reference_total > 0
        else None,
        missing_final_exit_attempt_lots=sum(not r["final_session_exit_attempt"] for r in rows),
        class_counts={kind: sum(r["valuation_class"] == kind for r in rows) for kind in CLASSES},
        raw_share_ready=False,
        revision_safe=False,
    )
    return dict(summary=summary, lots=rows, reasons=reasons, sensitivities=scenarios)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False, ensure_ascii=True) + "\n")


def main():
    import duckdb
    import pandas as pd

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-run-sha256", required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(repo):
        raise ValueError("output must be a new external directory")
    receipt_path = args.run / "receipt.json"
    receipt_hash = digest(receipt_path)
    if receipt_hash != args.expected_run_sha256:
        raise ValueError("unexpected frozen run receipt")
    receipt = json.loads(receipt_path.read_text())
    checked = {str(receipt_path): receipt_hash}

    def verified(relative):
        path = args.run / relative
        expected = receipt["outputs"][relative]
        if digest(path) != expected:
            raise ValueError("frozen artifact changed: " + relative)
        checked[str(path)] = expected
        return path

    source = json.loads(verified("summary.json").read_text())
    if source["status"] != "completed_unpublished_proxy_checkpoint" or source["pilot"]:
        raise ValueError("completed full frozen ledger required")
    portfolios = source["portfolios"]
    expected_keys = {
        (m, q, s)
        for m in ("pb_parent", "pe_deducted_proxy")
        for q in range(1, 6)
        for s in ("touch0", "touch10", "touch30", "close10")
    }
    keys = {(p["metric"], p["quintile"], p["scenario"]) for p in portfolios}
    if len(portfolios) != 40 or keys != expected_keys:
        raise ValueError("original forty portfolios required")
    con = duckdb.connect(":memory:")
    con.execute("SET threads=2")
    con.execute("SET memory_limit='512MB'")
    results = []
    for p in portfolios:
        folder = p["portfolio"]
        if folder != f"{p['metric']}_q{p['quintile']}_{p['scenario']}":
            raise ValueError("unexpected portfolio path identifier")
        holdings_path = verified(folder + "/holdings.parquet")
        orders_path = verified(folder + "/orders.parquet")
        daily_path = verified(folder + "/daily.csv")
        daily = pd.read_csv(daily_path, dtype={"date": str})
        sessions = daily.date.tolist()
        if len(sessions) != p["sessions"]:
            raise ValueError("daily session count differs")
        if not close(float(daily.iloc[-1]["cash"]), p["final"]["cash"]):
            raise ValueError("terminal cash differs from daily ledger")
        history = con.execute(
            """
            SELECT lot_id, arg_max(mark_price,date) AS price, max(date) AS date
            FROM read_parquet(?)
            WHERE mark_source='observed_adjusted_close'
              AND mark_price IS NOT NULL AND isfinite(mark_price) AND mark_price>0
            GROUP BY lot_id
        """,
            [str(holdings_path)],
        ).fetchdf()
        anchors = {
            r.lot_id: {"price": float(r.price), "date": r.date}
            for r in history.itertuples(index=False)
        }
        held = con.execute(
            "SELECT * FROM read_parquet(?) WHERE date=?", [str(holdings_path), p["last_date"]]
        ).fetchdf()
        attempts = con.execute(
            """
            SELECT lot_id,date,status,reason FROM read_parquet(?)
            WHERE side='sell' AND date<=?
            QUALIFY row_number() OVER(PARTITION BY lot_id ORDER BY date DESC)=1
        """,
            [str(orders_path), p["last_date"]],
        ).fetchdf()
        orders = {
            r.lot_id: dict(
                date=r.date, status=r.status, reason=r.reason if pd.notna(r.reason) else None
            )
            for r in attempts.itertuples(index=False)
        }
        # Convert nullable pandas scalars to ordinary None for portable JSON.
        records = held.astype(object).where(pd.notna(held), None).to_dict("records")
        result = terminal_analysis(p, records, anchors, orders, sessions)
        results.append(result)
        print(
            "analyzed",
            folder,
            "held",
            len(records),
            "unknown_reference",
            result["summary"]["unknown_reference_lots"],
            flush=True,
        )
    con.close()
    # Fail before writing if any input or the receipt changed during analysis.
    for path, expected in checked.items():
        if digest(path) != expected:
            raise ValueError("source changed during analysis")
    output.mkdir(parents=True)
    summaries = [r["summary"] for r in results]
    lots = [x for r in results for x in r["lots"]]
    reasons = [x for r in results for x in r["reasons"]]
    sensitivities = [x for r in results for x in r["sensitivities"]]
    pd.DataFrame(lots).to_parquet(output / "private_terminal_lots.parquet", index=False)
    pd.DataFrame(summaries).drop(columns="class_counts").to_csv(
        output / "portfolio_summary.csv", index=False
    )
    pd.DataFrame(reasons).to_csv(output / "valuation_and_exit_reasons.csv", index=False)
    pd.DataFrame(sensitivities).to_csv(output / "valuation_sensitivities.csv", index=False)
    write_json(
        output / "summary.json",
        dict(
            status="completed_readonly_valuation_sensitivity",
            terminal_date=portfolios[0]["last_date"],
            portfolios=summaries,
            sensitivity_rows=len(sensitivities),
            no_transactions=True,
            raw_share_ready=False,
            revision_safe=False,
        ),
    )
    write_json(output / "sensitivities.json", sensitivities)
    lines = [
        "# 未退出资产及最后有效价值敏感性",
        "",
        "本分析只读复用冻结账本，未重跑组合，未增加交易、现金或改变持仓单位。",
        "",
        "最后有效锚点取各 lot 历史账本中最近一次 observed_adjusted_close 的正有限价格，并核对终期保存的 last_observed 字段。未采用终止报价后的供应商报价、未来回填或任意最近报价。",
        "",
        "估值原因与最后卖单失败原因分别保留。当前有价仍未退出，与终期缺价、退市未决分别计数；最后拒因不是完整因果解释。报价年龄按已存日账本的交易日序列计算，同时列日历天数。",
        "",
        "A 情景仅给未定价资产最后有效参考值乘以 0/50/100%，当前有价的未退出资产保留当前估值；A 的 0% 逐组合复现原 zero_unresolved_nav。B 情景给全部仍持有资产的参考值乘以 0/50/100%，有价资产以当前价格为参考。",
        "",
        "两类情景都不产生现金，不是回收概率、可实现收益或价值上下界。参考值比例分别除以初始资本及现金＋当前可估持仓＋未定价资产最后参考值；后者仅是参考总值，绝非正式 NAV 权重。",
        "",
        "没有有效历史锚点时保留 unknown。0% 是明确全部减值假设且仍报告未知数量；50/100% 总值及完整参考权重留空，同时另列已知部分，不把未知金额填零后隐去。",
        "",
        "| 组合 | 持有 lot | 终期未定价 | 有价未退出 | 无有效锚点 | 未定价最后参考值/初始资本 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for s in summaries:
        weight = s["unpriced_reference_weight_initial"]
        shown = "unknown" if weight is None else f"{weight:.4%}"
        lines.append(
            f"| {s['portfolio']} | {s['holding_lots']} | {s['unpriced_lots']} | "
            f"{s['valued_but_unexited_lots']} | {s['unknown_reference_lots']} | {shown} |"
        )
    lines.extend(
        [
            "",
            "逐 lot 身份和金额只保存在本外部目录的 private_terminal_lots.parquet。聚合 CSV/JSON 保留全部 40 组合、两类估值范围和 240 个情景行，未丢弃难处理资产。",
            "",
            "历史修订仍不安全（revision_safe=false）；复权单位不等于法定股数，真实公司行动与退市回收仍未认证。分组间资产可能重复，跨组合加总不是一个可投资账户。",
            "",
        ]
    )
    (output / "method_and_results.zh-CN.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(
        output / "receipt.json",
        dict(
            status="completed_readonly_valuation_sensitivity",
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            run_receipt_sha256=receipt_hash,
            source_sha256=digest(__file__),
            inputs=checked,
            portfolios=40,
            terminal_lot_rows=len(lots),
            sensitivity_rows=len(sensitivities),
            no_transactions=True,
            outputs={
                str(p.relative_to(output)): digest(p) for p in output.iterdir() if p.is_file()
            },
        ),
    )
    print("completed", output, flush=True)


if __name__ == "__main__":
    main()
