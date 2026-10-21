#!/usr/bin/env python3
"""Read-only additive attribution of frozen adjusted-unit portfolio ledgers."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


INITIAL = 1_000_000.0
TOL = 0.000001
PNL = [f"net_pnl_{v}" for v in ("0", "50", "100", "strict")]
META = ["portfolio", "metric", "quintile", "scenario"]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def json_write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def equal(actual, expected, message):
    error = np.abs(np.asarray(actual, dtype=float) - np.asarray(expected, dtype=float))
    require(bool(np.isfinite(error).all() and (error <= TOL).all()), message)
    return float(error.max()) if error.size else 0.0


def nullable_sum(values):
    return None if values.isna().any() else float(values.sum())


def cash_exposure(daily, initial=INITIAL):
    """Prior observed closing cash earns ACT/365 simple interest; first interval is zero.

    Calendar intervals are split at January 1. Cash is never reinvested, and no
    causal missed-stock return or interest beyond the terminal date is asserted.
    """
    rows, years = [], {}
    previous = None
    for row in daily.to_dict("records"):
        day = datetime.strptime(row["date"], "%Y%m%d")
        amount = 0.0
        days = 0
        if previous is not None:
            start, cash = previous
            require(day > start, "daily dates must be sorted and unique")
            while start < day:
                stop = min(day, datetime(start.year + 1, 1, 1))
                gap = (stop - start).days
                piece = cash * gap / 365.0
                years[start.year] = years.get(start.year, 0.0) + piece
                amount += piece
                days += gap
                start = stop
        strict = row["strict_nav"]
        zero = row["zero_unresolved_nav"]
        rows.append(dict(
            date=row["date"], cash=row["cash"], cash_fraction_initial=row["cash"] / initial,
            cash_fraction_strict_nav=row["cash"] / strict
            if pd.notna(strict) and strict > 0 else None,
            cash_fraction_zero_valuation=row["cash"] / zero if zero > 0 else None,
            preceding_calendar_days=days, cash_year_exposure=amount,
            interest_per_1pct_simple=amount * 0.01,
            strict_nav_available=pd.notna(strict),
        ))
        previous = day, float(row["cash"])
    return pd.DataFrame(rows), years


def aggregate(frame, keys):
    """Additive contribution aggregation; strict unknowns never disappear in sums."""
    columns = PNL + ["buy_notional", "sell_notional", "buy_fee", "sell_fee",
                     "terminal_value_0", "unpriced_reference_known_component"]
    grouped = frame.groupby(keys, sort=True, dropna=False)
    result = grouped[columns].sum().reset_index()
    for column in PNL:
        missing = grouped[column].apply(lambda x: bool(x.isna().any())).to_numpy()
        result.loc[missing, column] = np.nan
    result["planned_members"] = grouped.size().to_numpy()
    result["filled_buys"] = grouped.buy_filled.sum().to_numpy()
    result["failed_buys"] = result.planned_members - result.filled_buys
    result["zero_budget_members"] = grouped.budget_positive.apply(lambda x: int((~x).sum())).to_numpy()
    result["terminal_unpriced_lots"] = grouped.terminal_unpriced.sum().to_numpy()
    result["unknown_reference_lots"] = grouped.unknown_reference.sum().to_numpy()
    result["unpriced_reference_value"] = result.unpriced_reference_known_component
    result.loc[result.unknown_reference_lots.gt(0), "unpriced_reference_value"] = np.nan
    for suffix in ("0", "50", "100", "strict"):
        result[f"contribution_initial_{suffix}"] = result[f"net_pnl_{suffix}"] / INITIAL
    return result


def attribute_portfolio(portfolio, members, orders, daily, boundaries, terminal):
    """Decompose a single persisted path, with no quote fetching or strategy replay."""
    daily = daily.copy()
    daily["date"] = daily.date.astype(str)
    require(daily.date.tolist() == sorted(set(daily.date)), "invalid daily calendar")
    require(len(daily) == portfolio["sessions"], "daily session count")
    require(daily.iloc[-1].date == portfolio["last_date"], "terminal date mismatch")
    for col in ("cash", "known_marked_value", "zero_unresolved_nav", "cumulative_fees"):
        require(np.isfinite(daily[col]).all(), "nonfinite daily " + col)
    require(daily.cash.ge(-TOL).all(), "negative cash")
    equal(daily.cash + daily.known_marked_value, daily.zero_unresolved_nav, "daily value identity")
    require((daily.strict_nav.isna() == daily.unresolved_lots.gt(0)).all(), "strict availability")
    equal(daily.strict_nav.dropna(), daily.loc[daily.strict_nav.notna(), "zero_unresolved_nav"],
          "strict known value")
    require(set(orders.side) <= {"buy", "sell"}, "unexpected order side")
    require(set(orders.date) <= set(daily.date), "order outside persisted calendar")
    require(set(orders.status) <= {"filled", "expired", "pending"}, "unexpected order status")
    filled = orders.loc[orders.status.eq("filled")].copy()
    unfilled = orders.loc[orders.status.ne("filled")]
    for col in ("notional", "fee", "units"):
        require(np.isfinite(orders[col]).all(), "nonfinite order " + col)
        require(orders[col].ge(0).all(), "negative order " + col)
        equal(unfilled[col], np.zeros(len(unfilled)), "unfilled economic activity")
    require(filled.price.gt(0).all() and np.isfinite(filled.price.to_numpy(dtype=float)).all(),
            "invalid fill price")
    equal(filled.notional, filled.units * filled.price, "fill notional identity")
    buys = orders.loc[orders.side.eq("buy")].copy().rename(columns={"cohort": "entry_date"})
    sells = filled.loc[filled.side.eq("sell")].copy()
    require(not buys.duplicated(["entry_date", "symbol"]).any(), "duplicate buy membership")
    require(not buys.lot_id.duplicated().any(), "duplicate buy lot")
    require(not sells.lot_id.duplicated().any(), "multiple sales for same full lot")
    require(buys.date.eq(buys.entry_date).all(), "buy date differs from entry")
    require(set(buys.status) <= {"filled", "expired"}, "invalid buy status")
    require(np.isfinite(buys.budget).all() and buys.budget.ge(0).all(), "invalid slot budget")
    require(members.formation_date.lt(members.entry_date).all(), "formation not before entry")
    require(not members.duplicated(["entry_date", "symbol"]).any(), "duplicate member identity")
    require(members.groupby("entry_date").formation_date.nunique().eq(1).all(),
            "entry maps to multiple formations")
    require(len(members) == portfolio["original_member_months"], "original member count")
    member_keys = members[["formation_date", "entry_date", "symbol"]]
    joined = member_keys.merge(buys, on=["entry_date", "symbol"], how="outer",
                               validate="one_to_one", indicator=True)
    require(joined._merge.eq("both").all(), "members and buy orders not one-to-one")
    joined = joined.drop(columns="_merge")
    sell_net = sells.assign(net=sells.notional - sells.fee).groupby("date").net.sum()
    prior_cash = daily.set_index("date").cash.shift(1, fill_value=INITIAL)
    counts = members.groupby("entry_date").size()
    reconstruction = (prior_cash.reindex(counts.index) + sell_net.reindex(counts.index, fill_value=0)) / counts
    expected = joined.entry_date.map(reconstruction)
    budget_error = equal(joined.budget, expected, "intended budget reconstruction mismatch")
    bought = joined.status.eq("filled")
    fill_budget_error = equal(joined.loc[bought, "notional"] + joined.loc[bought, "fee"],
                              expected.loc[bought], "filled cost differs from slot budget")
    require(set(sells.lot_id) <= set(joined.loc[bought, "lot_id"]), "sell without filled buy")
    by_lot = joined.set_index("lot_id")
    if len(sells):
        buy_lookup = by_lot.loc[sells.lot_id]
        require((sells.symbol.to_numpy() == buy_lookup.symbol.to_numpy()).all(), "sell symbol changed")
        require((sells.cohort.to_numpy() == buy_lookup.entry_date.to_numpy()).all(), "sell cohort changed")
        require((sells.date.to_numpy() > buy_lookup.entry_date.to_numpy()).all(), "same-day/pre-entry sale")
        equal(sells.units, buy_lookup.units, "sold units differ from purchased units")
    # Independent end-of-day cash reconstruction using only existing cash flows.
    cash_events = filled.assign(delta=np.where(filled.side.eq("sell"),
                                               filled.notional - filled.fee,
                                               -filled.notional - filled.fee))
    change = cash_events.groupby("date").delta.sum().reindex(daily.date, fill_value=0)
    cash_error = equal(INITIAL + change.cumsum().to_numpy(), daily.cash, "cash flow reconciliation")
    fees = filled.groupby("date").fee.sum().reindex(daily.date, fill_value=0).cumsum()
    equal(fees, daily.cumulative_fees, "fee reconciliation")
    require(not terminal.lot_id.duplicated().any(), "duplicate terminal reference lot")
    final_hold = boundaries.loc[boundaries.date.eq(portfolio["last_date"])].copy()
    require(not final_hold.lot_id.duplicated().any(), "duplicate terminal holding")
    require(set(terminal.lot_id) == set(final_hold.lot_id), "terminal reference inventory differs")
    require(set(final_hold.lot_id) == set(joined.loc[bought, "lot_id"]) - set(sells.lot_id),
            "bought/sold/open partition differs")
    for row in final_hold.itertuples(index=False):
        require(row.symbol == by_lot.loc[row.lot_id, "symbol"], "held symbol changed")
        equal(row.units, by_lot.loc[row.lot_id, "units"], "held units changed")
    t = terminal.set_index("lot_id")
    for h in final_hold.itertuples(index=False):
        r = t.loc[h.lot_id]
        require(h.symbol == r.symbol and h.cohort == r.cohort, "reference identity differs")
        equal(h.units, r.units, "reference units differ")
        require(r.terminal_date == portfolio["last_date"], "nonterminal reference")
        if pd.isna(h.marked_value):
            require(r.valuation_class in {"terminal_unsettled", "missing_terminal_quote"},
                    "unpriced class differs")
            if pd.notna(r.reference_value):
                require(r.last_valid_date <= portfolio["last_date"], "future terminal reference")
                equal(r.reference_value, h.units * r.last_valid_price, "terminal reference identity")
        else:
            require(r.valuation_class == "valued_exit_blocked", "valued class differs")
            equal(h.marked_value, r.current_marked_value, "current reference differs")
    result = joined[["formation_date", "entry_date", "symbol", "lot_id"]].copy()
    for key in META:
        result[key] = portfolio[key]
    result["formation_month"] = result.formation_date.str[:6]
    result["buy_filled"] = bought
    result["buy_status"] = joined.status
    result["buy_reason"] = joined.reason
    result["intended_slot_budget"] = joined.budget
    result["budget_verified"] = True
    result["budget_positive"] = result.intended_slot_budget.gt(0)
    result["buy_notional"] = joined.notional
    result["buy_fee"] = joined.fee
    sx = sells.set_index("lot_id")
    result["sell_notional"] = result.lot_id.map(sx.notional).fillna(0)
    result["sell_fee"] = result.lot_id.map(sx.fee).fillna(0)
    result["exit_date"] = result.lot_id.map(sx.date)
    fx = final_hold.set_index("lot_id")
    result["terminal_held"] = result.lot_id.isin(fx.index)
    result["terminal_unpriced"] = result.lot_id.isin(fx.index[fx.marked_value.isna()])
    result["terminal_value_0"] = result.lot_id.map(fx.marked_value).fillna(0)
    result["terminal_reference_value"] = result.lot_id.map(t.reference_value)
    result["terminal_valuation_class"] = result.lot_id.map(t.valuation_class)
    result["unknown_reference"] = result.terminal_unpriced & result.terminal_reference_value.isna()
    result["unpriced_reference_known_component"] = np.where(
        result.terminal_unpriced, result.terminal_reference_value.fillna(0), 0)
    result["net_pnl_0"] = (result.sell_notional - result.buy_notional - result.buy_fee
                            - result.sell_fee + result.terminal_value_0)
    for suffix, rate in (("50", 0.5), ("100", 1.0)):
        result[f"net_pnl_{suffix}"] = result.net_pnl_0 + rate * result.unpriced_reference_known_component
        result.loc[result.unknown_reference, f"net_pnl_{suffix}"] = np.nan
    result["net_pnl_strict"] = result.net_pnl_0.where(~result.terminal_unpriced)
    for suffix in ("0", "50", "100", "strict"):
        result[f"return_per_intended_budget_{suffix}"] = (
            result[f"net_pnl_{suffix}"] / result.intended_slot_budget.where(result.budget_positive))
        result[f"contribution_initial_{suffix}"] = result[f"net_pnl_{suffix}"] / INITIAL
    net_error = equal(result.net_pnl_0.sum(), daily.iloc[-1].zero_unresolved_nav - INITIAL,
                      "lot P0 does not reconcile")
    equal(result.buy_fee.sum() + result.sell_fee.sum(), daily.iloc[-1].cumulative_fees,
          "lot fees do not reconcile")
    strict_sum = nullable_sum(result.net_pnl_strict)
    if pd.notna(daily.iloc[-1].strict_nav):
        equal(strict_sum, daily.iloc[-1].strict_nav - INITIAL, "strict terminal contribution")
    else:
        require(strict_sum is None, "unknown strict terminal contribution was filled")
    # Annual occurrence attribution with both opening and closing values for each lot.
    annual_lots, annual = [], []
    prior = pd.DataFrame(columns=boundaries.columns).set_index("lot_id")
    previous_nav = INITIAL
    previous_strict = INITIAL
    for year, d in daily.groupby(daily.date.str[:4], sort=True):
        end = d.iloc[-1]
        current = boundaries.loc[boundaries.date.eq(end.date)].set_index("lot_id")
        require(not current.index.duplicated().any(), "duplicate annual boundary lot")
        equal(current.marked_value.fillna(0).sum(), end.known_marked_value, "year-end holdings value")
        require(int(current.marked_value.isna().sum()) == end.unresolved_lots,
                "year-end unresolved count")
        activity = filled.loc[filled.date.str[:4].eq(year)]
        active = set(activity.lot_id) | set(prior.index) | set(current.index)
        a = result.loc[result.lot_id.isin(active), META + ["lot_id", "symbol", "formation_date", "entry_date"]].copy()
        require(len(a) == len(active), "annual lot without original membership")
        a["year"] = int(year)
        a["opening_value_0"] = a.lot_id.map(prior.marked_value).fillna(0)
        a["closing_value_0"] = a.lot_id.map(current.marked_value).fillna(0)
        missing = (a.lot_id.isin(prior.index[prior.marked_value.isna()])
                   | a.lot_id.isin(current.index[current.marked_value.isna()]))
        for side in ("buy", "sell"):
            part = activity.loc[activity.side.eq(side)].set_index("lot_id")
            a[f"{side}_notional"] = a.lot_id.map(part.notional).fillna(0)
            a[f"{side}_fee"] = a.lot_id.map(part.fee).fillna(0)
        a["net_pnl_0"] = (a.closing_value_0 - a.opening_value_0 + a.sell_notional
                           - a.buy_notional - a.buy_fee - a.sell_fee)
        a["net_pnl_strict"] = a.net_pnl_0.where(~missing)
        annual_error = equal(a.net_pnl_0.sum(), end.zero_unresolved_nav - previous_nav,
                             "annual carried P0 does not reconcile")
        if pd.notna(previous_strict) and pd.notna(end.strict_nav):
            equal(nullable_sum(a.net_pnl_strict), end.strict_nav - previous_strict,
                  "strict annual boundary identity")
        else:
            require(nullable_sum(a.net_pnl_strict) is None, "unknown annual boundary hidden")
        annual.append(dict(**{k: portfolio[k] for k in META}, year=int(year),
                           start_date=d.iloc[0].date, end_date=end.date,
                           opening_value_0=previous_nav, closing_value_0=end.zero_unresolved_nav,
                           net_pnl_0=float(a.net_pnl_0.sum()),
                           net_pnl_strict=nullable_sum(a.net_pnl_strict),
                           buy_fees=float(a.buy_fee.sum()), sell_fees=float(a.sell_fee.sum()),
                           strict_unknown_days=int(d.strict_nav.isna().sum()),
                           contribution_initial_0=float(a.net_pnl_0.sum() / INITIAL),
                           reconciliation_error=annual_error))
        annual_lots.append(a)
        prior, previous_nav, previous_strict = current, end.zero_unresolved_nav, end.strict_nav
    annual_lots = pd.concat(annual_lots, ignore_index=True)
    lot_annual_sums = annual_lots.groupby("lot_id").net_pnl_0.sum()
    equal(result.loc[result.buy_filled, "net_pnl_0"],
          result.loc[result.buy_filled, "lot_id"].map(lot_annual_sums), "annual lots telescope")
    cash, years = cash_exposure(daily)
    for key in META:
        cash[key] = portfolio[key]
    for row in annual:
        row["cash_year_exposure"] = years.get(row["year"], 0.0)
        row["interest_per_1pct_simple"] = row["cash_year_exposure"] * 0.01
        row["daily_mean_cash_fraction_initial"] = float(
            cash.loc[cash.date.str[:4].eq(str(row["year"])), "cash_fraction_initial"].mean())
    summary = dict(**{k: portfolio[k] for k in META}, planned_members=len(result),
                   filled_buys=int(bought.sum()), failed_buys=int((~bought).sum()),
                   failed_buy_fraction=float((~bought).mean()),
                   zero_budget_members=int((~result.budget_positive).sum()),
                   terminal_unpriced_lots=int(result.terminal_unpriced.sum()),
                   unknown_reference_lots=int(result.unknown_reference.sum()),
                   buy_fees=float(result.buy_fee.sum()), sell_fees=float(result.sell_fee.sum()),
                   terminal_cash=float(daily.iloc[-1].cash),
                   terminal_current_value=float(result.terminal_value_0.sum()),
                   terminal_unpriced_buy_notional=float(result.loc[result.terminal_unpriced, "buy_notional"].sum()),
                   terminal_unpriced_buy_fees=float(result.loc[result.terminal_unpriced, "buy_fee"].sum()),
                   closed_lot_net_pnl=float(result.loc[result.buy_filled & ~result.terminal_held, "net_pnl_0"].sum()),
                   terminal_lot_net_pnl_0=float(result.loc[result.terminal_held, "net_pnl_0"].sum()),
                   unpriced_reference_known_component=float(result.unpriced_reference_known_component.sum()),
                   cash_year_exposure=float(cash.cash_year_exposure.sum()),
                   interest_per_1pct_simple=float(cash.interest_per_1pct_simple.sum()),
                   daily_mean_cash_fraction_initial=float(cash.cash_fraction_initial.mean()),
                   strict_unknown_days=int(daily.strict_nav.isna().sum()),
                   budget_reconstruction_max_error=budget_error,
                   filled_budget_max_error=fill_budget_error, cash_max_error=cash_error,
                   net_pnl_max_error=net_error, raw_share_ready=False, revision_safe=False)
    for column in PNL:
        summary[column] = nullable_sum(result[column])
        summary[column.replace("net_pnl", "contribution_initial")] = (
            None if summary[column] is None else summary[column] / INITIAL)
    summary["gross_pnl_0_same_path"] = summary["net_pnl_0"] + summary["buy_fees"] + summary["sell_fees"]
    return dict(members=result, lots=result.loc[result.buy_filled].copy(),
                symbols=aggregate(result, META + ["symbol"]),
                months=aggregate(result, META + ["formation_date", "formation_month", "entry_date"]),
                annual_lots=annual_lots, annual=annual, cash=cash, summary=summary)


def select_cases(symbols, contrasts):
    candidates, picks, by_symbol = [], [], {}
    for metric, left, right in contrasts:
        block = symbols.loc[symbols.metric.eq(metric) & symbols.scenario.eq("touch10")]
        a, b = (block.loc[block.quintile.eq(q)].set_index("symbol") for q in (left, right))
        joined = a[["net_pnl_0", "unpriced_reference_value"]].join(
            b[["net_pnl_0", "unpriced_reference_value"]], how="outer", lsuffix="_q1", rsuffix="_comparison")
        # Fill absent arms only, never an unknown reference of an existing arm.
        for arm, source in (("q1", a), ("comparison", b)):
            absent = ~joined.index.isin(source.index)
            joined.loc[absent, [f"net_pnl_0_{arm}", f"unpriced_reference_value_{arm}"]] = 0.0
        require(joined[["unpriced_reference_value_q1", "unpriced_reference_value_comparison"]].notna().all().all(),
                "unknown reference prevents exhaustive risk ranking")
        joined["pnl0_difference"] = joined.net_pnl_0_q1 - joined.net_pnl_0_comparison
        joined["unresolved_reference_both_arms"] = (joined.unpriced_reference_value_q1
                                                    + joined.unpriced_reference_value_comparison)
        joined = joined.reset_index()
        joined["metric"], joined["left_quintile"], joined["comparison_quintile"] = metric, left, right
        joined["scenario"] = "touch10"
        candidates.append(joined)
        for role, column, positive, ascending in (
            ("positive_gap", "pnl0_difference", True, False),
            ("negative_gap", "pnl0_difference", False, True),
            ("unresolved_reference", "unresolved_reference_both_arms", True, False),
        ):
            eligible = joined.loc[joined[column].gt(0) if positive else joined[column].lt(0)]
            eligible = eligible.sort_values([column, "symbol"], ascending=[ascending, True])
            reason = dict(metric=metric, left_quintile=left, comparison_quintile=right, role=role)
            if eligible.empty:
                picks.append(dict(**reason, symbol=None, selection_status="no_eligible_candidate"))
                continue
            winner = eligible.iloc[0]
            reason.update(pnl0_difference=float(winner.pnl0_difference),
                          unresolved_reference_both_arms=float(winner.unresolved_reference_both_arms))
            picks.append(dict(**reason, symbol=winner.symbol, selection_status="selected"))
            if winner.symbol not in by_symbol:
                by_symbol[winner.symbol] = dict(symbol=winner.symbol, selection_order=len(by_symbol) + 1,
                                               reasons=[])
            by_symbol[winner.symbol]["reasons"].append(reason)
    return pd.concat(candidates, ignore_index=True), dict(
        contrast_direction="q1_minus_comparator", deduplication="retain_reasons_no_backfill",
        slots=picks, cases=list(by_symbol.values()))


class ParquetOutputs:
    def __init__(self, output):
        self.output, self.writers = output, {}

    def append(self, name, frame):
        import pyarrow as pa
        import pyarrow.parquet as pq

        table = pa.Table.from_pandas(frame, preserve_index=False)
        # All-null object columns otherwise become Arrow null in one portfolio
        # and string in another. Contract string columns are explicit.
        text_columns = {"portfolio", "metric", "scenario", "symbol", "lot_id", "formation_date",
                        "entry_date", "formation_month", "buy_status", "buy_reason", "exit_date",
                        "terminal_valuation_class", "date"}
        fields = [pa.field(f.name, pa.string() if f.name in text_columns else f.type) for f in table.schema]
        table = table.cast(pa.schema(fields))
        if name not in self.writers:
            self.writers[name] = pq.ParquetWriter(self.output / name, table.schema, compression="zstd")
        table = table.cast(self.writers[name].schema)
        self.writers[name].write_table(table)

    def close(self):
        for writer in self.writers.values():
            writer.close()


def main():
    import duckdb

    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run", "unresolved", "members", "rules", "design-receipt", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--expected-rules-sha256", required=True)
    args = parser.parse_args()
    repo, output = Path(__file__).resolve().parents[1], args.output.resolve()
    require(not output.exists() and not output.is_relative_to(repo), "new external output required")
    checked = {}

    def verify(path, expected=None):
        actual = digest(path)
        require(expected is None or actual == expected, "source hash mismatch: " + str(path))
        checked[str(path)] = actual
        return actual

    rules_hash = verify(args.rules, args.expected_rules_sha256)
    rules = json.loads(args.rules.read_text())
    verify(args.design_receipt)
    design = json.loads(args.design_receipt.read_text())
    require(design["status"] == "rules_frozen_before_new_analysis", "unfrozen design")
    require(design["inputs"][str(args.rules)] == rules_hash, "design does not bind rules")
    require(rules["attribution"]["initial_capital"] == INITIAL and
            rules["attribution"]["valuation_fractions"] == [0, 0.5, 1] and
            rules["attribution"]["reconciliation_absolute_tolerance"] == TOL,
            "unsupported attribution rules")
    run_hash = verify(args.run / "receipt.json", rules["source_run_receipt_sha256"])
    receipt = json.loads((args.run / "receipt.json").read_text())
    unresolved_hash = verify(args.unresolved / "receipt.json",
                             design["inputs"][str(args.unresolved / "receipt.json")])
    ur = json.loads((args.unresolved / "receipt.json").read_text())
    require(ur["run_receipt_sha256"] == run_hash, "unresolved run differs")
    verify(args.members, receipt["inputs"][str(args.members)])
    require(checked[str(args.members)] == design["inputs"][str(args.members)], "design members differ")
    verify(args.run / "summary.json", receipt["outputs"]["summary.json"])
    source = json.loads((args.run / "summary.json").read_text())
    require(not source["pilot"] and source["status"] == "completed_unpublished_proxy_checkpoint",
            "completed nonpilot source required")
    expected = {(m, q, s) for m in ("pb_parent", "pe_deducted_proxy") for q in range(1, 6)
                for s in ("touch0", "touch10", "touch30", "close10")}
    portfolios = source["portfolios"]
    require(len(portfolios) == 40 and {(p["metric"], p["quintile"], p["scenario"])
                                     for p in portfolios} == expected, "all forty portfolios required")
    for p in portfolios:
        require(p["portfolio"] == f"{p['metric']}_q{p['quintile']}_{p['scenario']}", "unsafe portfolio path")
        for name in ("orders.parquet", "holdings.parquet", "daily.csv"):
            rel = p["portfolio"] + "/" + name
            verify(args.run / rel, receipt["outputs"][rel])
    for name in ("private_terminal_lots.parquet", "valuation_sensitivities.csv"):
        verify(args.unresolved / name, ur["outputs"][name])
    sources = [Path(__file__), repo / "tests/test_grouped_valuation_attribution.py", repo / "uv.lock"]
    source_hashes = {str(p.relative_to(repo)): digest(p) for p in sources}
    members = pd.read_parquet(args.members, columns=["ts_code", "group", "metric", "quintile",
                                                    "formation_date", "entry_date"])
    members = members.loc[members.group.eq("all_market")].rename(columns={"ts_code": "symbol"})
    terminal = pd.read_parquet(args.unresolved / "private_terminal_lots.parquet")
    sensitivities = pd.read_csv(args.unresolved / "valuation_sensitivities.csv")
    con = duckdb.connect(":memory:")
    con.execute("SET threads=2")
    con.execute("SET memory_limit='512MB'")
    output.mkdir(parents=True)
    sink = ParquetOutputs(output)
    summaries, annuals, primary_symbols = [], [], []
    try:
        for p in portfolios:
            root = args.run / p["portfolio"]
            daily = pd.read_csv(root / "daily.csv", dtype={"date": str})
            ends = daily.groupby(daily.date.str[:4]).date.max().tolist()
            boundaries = con.execute("SELECT * FROM read_parquet(?) WHERE date IN (SELECT unnest(?))",
                                     [str(root / "holdings.parquet"), ends]).fetchdf()
            result = attribute_portfolio(
                p, members.loc[members.metric.eq(p["metric"]) & members.quintile.eq(p["quintile"])],
                pd.read_parquet(root / "orders.parquet"), daily, boundaries,
                terminal.loc[terminal.portfolio.eq(p["portfolio"])])
            summary = result["summary"]
            for fraction, suffix in ((0, "0"), (0.5, "50"), (1, "100")):
                s = sensitivities.loc[sensitivities.portfolio.eq(p["portfolio"])
                                      & sensitivities.scope.eq("A_unpriced_only")
                                      & sensitivities.reference_fraction.eq(fraction)]
                require(len(s) == 1, "missing/duplicate sensitivity comparator")
                expected_value = s.iloc[0].scenario_value
                actual = summary[f"net_pnl_{suffix}"]
                if pd.isna(expected_value):
                    require(actual is None, "unknown sensitivity became known")
                else:
                    equal(actual + INITIAL, expected_value, "terminal sensitivity does not reconcile")
            for label, name in (("members", "private_member_outcomes.parquet"),
                                ("lots", "private_lot_attribution.parquet"),
                                ("symbols", "private_symbol_attribution.parquet"),
                                ("months", "private_formation_month_attribution.parquet"),
                                ("annual_lots", "private_lot_annual_attribution.parquet"),
                                ("cash", "daily_cash.parquet")):
                sink.append(name, result[label])
            for key in ("symbols", "months"):
                equal(result[key].net_pnl_0.sum(), summary["net_pnl_0"], key + " aggregation")
            summaries.append(summary)
            annuals.extend(result["annual"])
            if p["scenario"] == "touch10":
                primary_symbols.append(result["symbols"])
            print("attributed", p["portfolio"], "members", summary["planned_members"], flush=True)
    finally:
        sink.close()
        con.close()
    candidates, cases = select_cases(pd.concat(primary_symbols), rules["primary_contrasts"])
    candidates.to_parquet(output / "private_pair_symbol_differences.parquet", index=False)
    json_write(output / "private_selected_cases.json", cases)
    print("selected_cases", json.dumps(cases), flush=True)
    pd.DataFrame(summaries).to_csv(output / "portfolio_summary.csv", index=False)
    pd.DataFrame(annuals).to_csv(output / "annual_attribution.csv", index=False)
    json_write(output / "summary.json", dict(schema_version="grouped_valuation_attribution.v1",
               status="completed_readonly_attribution", portfolios=summaries,
               raw_share_ready=False, revision_safe=False, no_backtest_rerun=True))
    checks = dict(passed=True, portfolios=40, all_members_retained=True, budgets_verified=True,
                  zero_and_reference_sensitivities_reconciled=True,
                  annual_lot_and_portfolio_identities_reconciled=True,
                  strict_unknown_portfolios=sum(s["net_pnl_strict"] is None for s in summaries),
                  max_budget_error=max(s["budget_reconstruction_max_error"] for s in summaries),
                  max_cash_error=max(s["cash_max_error"] for s in summaries),
                  max_net_pnl_error=max(s["net_pnl_max_error"] for s in summaries), tolerance=TOL)
    json_write(output / "reconciliation.json", checks)
    (output / "method.zh-CN.md").write_text(
        "# 冻结账本贡献分解\n\n"
        "只读原40组合，不生成新交易。逐lot卖额减买额减费用加期末估值，归并逐股、形成月；"
        "发生年度按边界估值结转。formation_date来自原成员，entry_date不是形成日。\n\n"
        "0/50/100为未定价资产最后有效参考值乘指定比例，不是回收概率、现金、收益界限；"
        "严格贡献缺值保留。年度0估值遇缺价/恢复可能有大幅记账跳变，不当作真实损失/收益。\n\n"
        "成员接口保留全部计划名额；预算等于前日现金加当日旧仓卖出净款后除以原名额数，"
        "独立核对原budget及成功买单含费成本。未买且正预算回报0，零预算回报未知。\n\n"
        "现金实际收益0。cash_year_exposure按相邻交易日期间持有前一日收盘现金，"
        "ACT/365简单利率、跨年按日拆分、初日无前置区间；终日后不外推。每1%系数为"
        "暴露乘0.01，利息不再投资，是描述性叠加假设，不识别买不到股票的因果损失。"
        "日均现金率分母为固定初资，并非平均严格NAV权重。失败买单比例使用全部原名额。\n\n"
        "费用为本路径直接记账项；四情景间差异包含资金、持仓路径改变，不可称纯手续费。"
        "金额贡献除以初资得到可加总贡献比例，乘100才是百分点。\n\n"
        "案例按冻结Q1减比较组方向、touch10固定正差/负差/未决参考暴露规则；"
        "代码升序解平，顺序去重且保留理由，不补挑。全部身份只在private文件。\n\n"
        "revision_safe=false，raw_share_ready=false；本模型为复权单位假设，非真实股份或认证成交。\n",
        encoding="utf-8")
    for path, expected_hash in checked.items():
        require(digest(path) == expected_hash, "input changed during attribution: " + path)
    for rel, expected_hash in source_hashes.items():
        require(digest(repo / rel) == expected_hash, "source changed during attribution")
    json_write(output / "receipt.json", dict(
        schema_version="grouped_valuation_attribution.v1", status="completed_readonly_attribution",
        generated_at_utc=datetime.now(timezone.utc).isoformat(), run_receipt_sha256=run_hash,
        unresolved_receipt_sha256=unresolved_hash, rules_sha256=rules_hash,
        inputs=checked, source_hashes=source_hashes,
        outputs={str(p.relative_to(output)): digest(p) for p in sorted(output.iterdir()) if p.is_file()},
        portfolios=40, member_rows=sum(s["planned_members"] for s in summaries),
        reconciliation_passed=True, no_backtest_rerun=True, raw_share_ready=False, revision_safe=False,
        resources="one portfolio at a time; DuckDB threads=2, memory_limit=512MB; BLAS=1"))
    print("completed", output, flush=True)


if __name__ == "__main__":
    main()
