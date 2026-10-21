"""Study-specific adjusted-unit ledger; deliberately not a raw-share simulator.

The general account/execution engine remains owned by quant-platform. This
diagnostic isolates cash retention, deferred exits and unresolved valuation for
the frozen grouped-valuation cohorts. See the accompanying method document.
"""

from __future__ import annotations

from collections import defaultdict
from math import isclose, isfinite


def positive(value):
    try:
        return isfinite(float(value)) and float(value) > 0
    except (TypeError, ValueError):
        return False


def block_reason(row, side, policy):
    if row is None or not positive(row.get("adj_close")):
        return "missing_price"
    if not positive(row.get("amount")):
        return "no_positive_amount"
    fields = ("is_suspended", "is_limit_up", "is_limit_down")
    if any(row.get(f) is None or str(row[f]) not in {"True", "False"} for f in fields):
        return "unknown_flags"
    if row["is_suspended"]:
        return "suspended"
    up = side == "buy"
    if row["is_limit_up" if up else "is_limit_down"]:
        return "upper_limit" if up else "lower_limit"
    if policy == "any_touch":
        field, limit = ("high", "up_limit") if up else ("low", "down_limit")
        if not positive(row.get(field)) or not positive(row.get(limit)):
            return "unknown_limit_price"
        if float(row[field]) >= float(row[limit]) if up else float(row[field]) <= float(row[limit]):
            return "upper_limit_touch" if up else "lower_limit_touch"
    return None


def run_ledger(
    days,
    get_quotes,
    cohorts,
    *,
    delist_dates=None,
    initial_cash=1_000_000.0,
    fee_bps=10.0,
    fill_policy="any_touch",
    liquidation_date=None,
    unit_mode="adjusted_units",
    corporate_actions=(),
    sink=None,
):
    """Run one independent long-only basket; optionally emit daily chunks to sink.

    A cohort is an entry-day -> original ordered unique member list mapping.
    Formation-day qualifications must be enforced upstream. No future eligibility
    filtering is allowed. Missing entries stay in the original denominator.
    """
    if unit_mode != "adjusted_units" or corporate_actions:
        raise ValueError("raw shares/action cash postings require certified action evidence")
    if not positive(initial_cash) or not isfinite(fee_bps) or not 0 <= fee_bps < 10000:
        raise ValueError("invalid initial cash or proportional fees")
    if fill_policy not in {"any_touch", "close_flag"}:
        raise ValueError("unknown fill policy")
    if not days or list(days) != sorted(set(days)):
        raise ValueError("calendar must be sorted, unique and nonempty")
    if set(cohorts) - set(days) or (liquidation_date and liquidation_date not in days):
        raise ValueError("order date outside calendar")
    if liquidation_date and any(d >= liquidation_date for d in cohorts):
        raise ValueError("cohort entry must precede final liquidation")
    if any(not names or len(names) != len(set(names)) for names in cohorts.values()):
        raise ValueError("empty or duplicate original cohort membership")
    delist_dates = delist_dates or {}
    cash, fees, lots = float(initial_cash), 0.0, {}
    result = {"daily": [], "holdings": [], "orders": []}
    rate = fee_bps / 10000

    for day in days:
        quotes = get_quotes(day)
        orders, holdings = [], []
        rebalancing = day in cohorts
        if rebalancing or (liquidation_date and day >= liquidation_date):
            for lot in lots.values():
                if lot["requested_date"] is None:
                    lot["requested_date"] = day
        # Persist the original request, even if a later cohort selects this name.
        for lot_id, lot in list(lots.items()):
            if lot["requested_date"] is None:
                continue
            symbol = lot["symbol"]
            terminal = bool(delist_dates.get(symbol) and day >= delist_dates[symbol])
            row = quotes.get(symbol)
            reason = "terminal_unsettled" if terminal else block_reason(row, "sell", fill_policy)
            price = float(row["adj_close"]) if not reason else None
            notional = lot["units"] * price if not reason else 0.0
            fee = notional * rate
            order = dict(
                date=day,
                lot_id=lot_id,
                symbol=symbol,
                cohort=lot["cohort"],
                requested_date=lot["requested_date"],
                side="sell",
                original_weight=lot["original_weight"],
                budget=None,
                units=lot["units"] if not reason else 0.0,
                requested_units=lot["units"],
                price=price,
                notional=notional,
                fee=fee,
                status="pending" if reason else "filled",
                reason=reason,
            )
            orders.append(order)
            if not reason:
                cash += notional - fee
                fees += fee
                del lots[lot_id]
        if rebalancing:
            names = cohorts[day]
            # Fixed before any buy attempt. Failed slots never augment other slots.
            budget = max(cash, 0.0) / len(names)
            pending_names = {x["symbol"] for x in lots.values() if x["requested_date"]}
            for ix, symbol in enumerate(names):
                lot_id = f"{day}:{ix}:{symbol}"
                row = quotes.get(symbol)
                terminal = bool(delist_dates.get(symbol) and day >= delist_dates[symbol])
                reason = (
                    "terminal_unsettled"
                    if terminal
                    else "pending_old_exit"
                    if symbol in pending_names
                    else "no_cash"
                    if budget <= 1e-12
                    else block_reason(row, "buy", fill_policy)
                )
                price = float(row["adj_close"]) if not reason else None
                notional = budget / (1 + rate) if not reason else 0.0
                fee = notional * rate
                units = notional / price if not reason else 0.0
                orders.append(
                    dict(
                        date=day,
                        lot_id=lot_id,
                        symbol=symbol,
                        cohort=day,
                        requested_date=day,
                        side="buy",
                        original_weight=1 / len(names),
                        budget=budget,
                        units=units,
                        requested_units=None,
                        price=price,
                        notional=notional,
                        fee=fee,
                        status="expired" if reason else "filled",
                        reason=reason,
                    )
                )
                if not reason:
                    cash -= notional + fee
                    fees += fee
                    lots[lot_id] = dict(
                        symbol=symbol,
                        cohort=day,
                        units=units,
                        original_weight=1 / len(names),
                        requested_date=None,
                        last_observed_price=price,
                        last_observed_date=day,
                    )
        if cash < -max(1e-7, initial_cash * 1e-10):
            raise AssertionError("negative scenario cash")
        known, unresolved = 0.0, 0
        for lot_id, lot in sorted(lots.items()):
            symbol = lot["symbol"]
            row = quotes.get(symbol)
            terminal = bool(delist_dates.get(symbol) and day >= delist_dates[symbol])
            observed = row is not None and positive(row.get("adj_close")) and not terminal
            price = float(row["adj_close"]) if observed else None
            source = (
                "observed_adjusted_close"
                if observed
                else "unresolved_terminal"
                if terminal
                else "unresolved_missing_quote"
            )
            if observed:
                lot["last_observed_price"] = price
                lot["last_observed_date"] = day
                known += lot["units"] * price
            else:
                unresolved += 1
            holdings.append(
                dict(
                    date=day,
                    lot_id=lot_id,
                    **lot,
                    mark_price=price,
                    mark_source=source,
                    marked_value=lot["units"] * price if observed else None,
                )
            )
        daily = dict(
            date=day,
            cash=cash,
            known_marked_value=known,
            holding_lots=len(lots),
            unresolved_lots=unresolved,
            unresolved_units=sum(h["units"] for h in holdings if h["mark_price"] is None),
            pending_exit_lots=sum(x["requested_date"] is not None for x in lots.values()),
            cumulative_fees=fees,
            strict_nav=None if unresolved else cash + known,
            zero_unresolved_nav=cash + known,
        )
        if sink:
            sink(daily, holdings, orders)
        else:
            result["daily"].append(daily)
            result["holdings"].extend(holdings)
            result["orders"].extend(orders)
    return result


class LedgerVerifier:
    """Independent replay from filled order records, checking each daily snapshot."""

    def __init__(self, initial_cash):
        self.initial = initial_cash
        self.cash = initial_cash
        self.fees = 0.0
        self.units = {}
        self.days = 0
        self.max_cash_error = 0.0

    def check(self, daily, holdings, orders):
        for order in orders:
            assert order["date"] == daily["date"]
            if order["status"] != "filled":
                assert order["units"] == order["fee"] == order["notional"] == 0
                assert order["reason"]
                continue
            assert order["reason"] is None and positive(order["price"])
            assert positive(order["units"]) and order["fee"] >= 0
            assert isclose(order["notional"], order["units"] * order["price"], rel_tol=1e-12)
            lot_id = order["lot_id"]
            if order["side"] == "buy":
                assert lot_id not in self.units
                self.units[lot_id] = order["units"]
                self.cash -= order["notional"] + order["fee"]
                assert isclose(order["budget"], order["notional"] + order["fee"], rel_tol=1e-12)
            else:
                assert isclose(self.units.pop(lot_id), order["units"], rel_tol=1e-12)
                self.cash += order["notional"] - order["fee"]
            self.fees += order["fee"]
        self.max_cash_error = max(self.max_cash_error, abs(self.cash - daily["cash"]))
        assert isclose(self.cash, daily["cash"], rel_tol=1e-10, abs_tol=1e-7)
        assert self.cash >= -self.initial * 1e-10
        assert isclose(self.fees, daily["cumulative_fees"], rel_tol=1e-10, abs_tol=1e-7)
        observed_units = {h["lot_id"]: h["units"] for h in holdings}
        assert len(observed_units) == len(holdings) and observed_units == self.units
        assert daily["holding_lots"] == len(holdings)
        known, missing = 0.0, 0
        for h in holdings:
            assert h["date"] == daily["date"]
            assert h["last_observed_date"] <= daily["date"]
            if h["mark_price"] is None:
                assert h["marked_value"] is None
                missing += 1
            else:
                assert h["mark_source"] == "observed_adjusted_close"
                assert h["last_observed_date"] == daily["date"]
                assert isclose(h["marked_value"], h["units"] * h["mark_price"], rel_tol=1e-12)
                known += h["marked_value"]
        assert missing == daily["unresolved_lots"]
        assert isclose(known, daily["known_marked_value"], rel_tol=1e-10, abs_tol=1e-7)
        assert isclose(self.cash + known, daily["zero_unresolved_nav"], rel_tol=1e-10, abs_tol=1e-7)
        assert (
            daily["strict_nav"] is None
            if missing
            else isclose(daily["strict_nav"], self.cash + known, rel_tol=1e-10, abs_tol=1e-7)
        )
        self.days += 1


def verify_ledger(result, initial_cash):
    orders, holdings = defaultdict(list), defaultdict(list)
    for row in result["orders"]:
        orders[row["date"]].append(row)
    for row in result["holdings"]:
        holdings[row["date"]].append(row)
    verifier = LedgerVerifier(initial_cash)
    for daily in result["daily"]:
        verifier.check(daily, holdings[daily["date"]], orders[daily["date"]])
    return {"days": verifier.days, "max_cash_error": verifier.max_cash_error}
