"""Research-only real-order benchmark and holdout diagnostics; no execution engine."""

from __future__ import annotations

import math
import re
import numpy as np
import pandas as pd

KINDS = ("actual", "paper", "synthetic")
STATES = ("filled", "cancelled", "expired", "rejected")


def _required(frame, columns):
    if not set(columns).issubset(frame.columns):
        raise ValueError(f"missing required columns: {set(columns) - set(frame.columns)}")


def _times(frame, columns):
    for column in columns:
        for value in frame[column]:
            if pd.isna(value) or (
                isinstance(value, str) and not re.search(r"(Z|[+-]\d{2}:\d{2})$", value)
            ):
                raise ValueError("timestamps must include an explicit UTC offset")
            if not isinstance(value, str) and pd.Timestamp(value).tzinfo is None:
                raise ValueError("naive timestamp")
        frame[column] = pd.to_datetime(frame[column], utc=True, errors="raise")


def _numbers(frame, columns, *, positive=False):
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        values = frame[column].to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values <= 0 if positive else values < 0).any():
            raise ValueError(f"invalid numeric values: {column}")


def _identities(frame, columns):
    for column in columns:
        if frame[column].isna().any() or frame[column].astype(str).str.strip().eq("").any():
            raise ValueError("empty identity")
        frame[column] = frame[column].astype(str)


def measure_orders(orders, fills, quotes, *, data_kind, max_quote_age_ms=1000):
    """Align only available past quotes; missing benchmarks remain ineligible.

    Parent fees are actual total CNY fees, counted once. Full shortfall uses
    decision midpoint and marks unfilled shares at terminal midpoint. It can be
    negative, and includes market/signal movement rather than causal own impact.
    """
    if data_kind not in KINDS or not math.isfinite(max_quote_age_ms) or max_quote_age_ms <= 0:
        raise ValueError("invalid evidence kind or quote freshness")
    o, f, q = orders.copy(), fills.copy(), quotes.copy()
    _required(
        o,
        [
            "parent_order_id",
            "symbol",
            "side",
            "target_qty",
            "decision_time",
            "arrival_time",
            "end_time",
            "state",
            "fees_cny",
        ],
    )
    _required(f, ["fill_id", "parent_order_id", "fill_time", "qty", "price"])
    _required(q, ["symbol", "quote_time", "bid", "ask"])
    _identities(o, ["parent_order_id", "symbol"])
    _identities(f, ["fill_id", "parent_order_id"])
    _identities(q, ["symbol"])
    if o.parent_order_id.duplicated().any() or f.fill_id.duplicated().any():
        raise ValueError("duplicate order or fill identity")
    if not o.side.isin(["buy", "sell"]).all() or not o.state.isin(STATES).all():
        raise ValueError("invalid side or nonterminal state")
    _times(o, ["decision_time", "arrival_time", "end_time"])
    _times(f, ["fill_time"])
    _times(q, ["quote_time"])
    if ((o.decision_time > o.arrival_time) | (o.arrival_time > o.end_time)).any():
        raise ValueError("inconsistent order lifecycle")
    if "predicted_arrival_bp" in o:
        _required(o, ["prediction_time"])
        _times(o, ["prediction_time"])
        if (
            o.prediction_time.gt(o.arrival_time).any()
            or not np.isfinite(pd.to_numeric(o.predicted_arrival_bp, errors="raise")).all()
        ):
            raise ValueError("invalid or future prediction")
    _numbers(o, ["target_qty"], positive=True)
    _numbers(o, ["fees_cny"])
    _numbers(f, ["qty", "price"], positive=True)
    _numbers(q, ["bid", "ask"], positive=True)
    if q.duplicated(["symbol", "quote_time"]).any() or q.bid.gt(q.ask).any():
        raise ValueError("duplicate or crossed quotes")
    if "available_time" in q:
        _times(q, ["available_time"])
        if q.available_time.lt(q.quote_time).any():
            raise ValueError("availability before exchange quote timestamp")
    else:
        q["available_time"] = q.quote_time
    if "market_level" in q:
        _numbers(q, ["market_level"], positive=True)
    if not f.parent_order_id.isin(o.parent_order_id).all():
        raise ValueError("orphan fills")
    quotes_by_symbol = {key: group.sort_values("quote_time") for key, group in q.groupby("symbol")}
    fills_by_order = {key: group for key, group in f.groupby("parent_order_id")}
    records = []
    for order in o.itertuples(index=False):
        executed = fills_by_order.get(order.parent_order_id, f.iloc[:0])
        qty = float(executed.qty.sum())
        if qty > order.target_qty + 1e-8 or (
            order.state == "filled" and not math.isclose(qty, order.target_qty, abs_tol=1e-8)
        ):
            raise ValueError("fill quantity does not reconcile with order")
        if order.state == "rejected" and qty > 0:
            raise ValueError("rejected order has fills")
        if (
            executed.fill_time.lt(order.arrival_time) | executed.fill_time.gt(order.end_time)
        ).any():
            raise ValueError("fill outside order lifecycle")
        source = quotes_by_symbol.get(order.symbol, q.iloc[:0])

        def quote_at(timestamp):
            past = source.loc[source.quote_time.le(timestamp) & source.available_time.le(timestamp)]
            if (
                past.empty
                or (timestamp - past.iloc[-1].quote_time).total_seconds() * 1000 > max_quote_age_ms
            ):
                return None
            return past.iloc[-1]

        references = {
            key: quote_at(getattr(order, key + "_time")) for key in ("decision", "arrival", "end")
        }
        mid = {
            key: None if value is None else float((value.bid + value.ask) / 2)
            for key, value in references.items()
        }
        sign = 1 if order.side == "buy" else -1
        notional = float((executed.qty * executed.price).sum())
        eligible = all(value is not None for value in mid.values())
        row = {
            "parent_order_id": order.parent_order_id,
            "symbol": order.symbol,
            "side": order.side,
            "arrival_time": order.arrival_time,
            "end_time": order.end_time,
            "state": order.state,
            "data_kind": data_kind,
            "target_qty": float(order.target_qty),
            "filled_qty": qty,
            "unfilled_qty": float(order.target_qty - qty),
            "fees_cny": float(order.fees_cny),
            "calibration_eligible": eligible,
            "missing_benchmarks": ",".join(key for key, value in mid.items() if value is None),
            "decision_execution_cny": np.nan,
            "opportunity_cny": np.nan,
            "shortfall_bp": np.nan,
            "arrival_execution_bp": np.nan,
            "delay_bp": np.nan,
        }
        if hasattr(order, "predicted_arrival_bp"):
            row["predicted_arrival_bp"] = float(order.predicted_arrival_bp)
        if mid["arrival"] is not None and qty > 0:
            row["arrival_execution_bp"] = sign * (notional / qty / mid["arrival"] - 1) * 10000
        if mid["decision"] is not None and mid["arrival"] is not None:
            row["delay_bp"] = sign * (mid["arrival"] / mid["decision"] - 1) * 10000
        if eligible:
            execution = sign * (notional - qty * mid["decision"])
            opportunity = sign * (order.target_qty - qty) * (mid["end"] - mid["decision"])
            row.update(
                decision_execution_cny=execution,
                opportunity_cny=opportunity,
                shortfall_bp=(execution + opportunity + order.fees_cny)
                / (order.target_qty * mid["decision"])
                * 10000,
            )
        for seconds in (30, 300, 1800):
            later = quote_at(order.end_time + pd.Timedelta(seconds=seconds))
            field = f"market_adjusted_response_{seconds}s_bp"
            row[field] = np.nan
            if later is not None and references["end"] is not None and "market_level" in q:
                row[field] = (
                    sign
                    * (
                        math.log(float((later.bid + later.ask) / 2) / mid["end"])
                        - math.log(
                            float(later.market_level) / float(references["end"].market_level)
                        )
                    )
                    * 10000
                )
        records.append(row)
    return pd.DataFrame(records)


def chronological_validation(frame, *, train_fraction=0.7, min_train_orders=20, min_test_orders=10):
    """Fit a training-only side median, then measure errors on later UTC dates.

    All fills belong to one parent row. Split entire arrival dates to prevent
    sibling/order-day leakage. Parent benchmark is arrival-time execution cost.
    """
    if not 0 < train_fraction < 1 or min_train_orders < 1 or min_test_orders < 1:
        raise ValueError("invalid validation limits")
    _required(
        frame,
        [
            "parent_order_id",
            "arrival_time",
            "end_time",
            "side",
            "arrival_execution_bp",
            "calibration_eligible",
            "data_kind",
        ],
    )
    if frame.parent_order_id.duplicated().any():
        raise ValueError("duplicate parent observation")
    if len(frame.data_kind.unique()) > 1 or not frame.data_kind.isin(KINDS).all():
        raise ValueError("mixed evidence cannot be pooled for calibration")
    eligible = frame.loc[
        frame.calibration_eligible & np.isfinite(frame.arrival_execution_bp)
    ].copy()
    if eligible.empty:
        return {"status": "insufficient_data", "train_orders": 0, "test_orders": 0}
    eligible["date"] = pd.to_datetime(eligible.arrival_time, utc=True).dt.strftime("%Y-%m-%d")
    days = sorted(eligible.date.unique())
    split = max(1, min(len(days) - 1, int(len(days) * train_fraction)))
    train = eligible.loc[eligible.date.isin(days[:split])]
    test = eligible.loc[eligible.date.isin(days[split:])]
    cutoff = None if test.empty else pd.to_datetime(test.arrival_time, utc=True).min()
    before = len(train)
    if cutoff is not None:
        train = train.loc[pd.to_datetime(train.end_time, utc=True).lt(cutoff)]
    purged = before - len(train)
    result = {
        "status": "insufficient_data",
        "purged_training_orders": purged,
        "train_orders": len(train),
        "test_orders": len(test),
        "train_end": None if train.empty else train.date.max(),
        "test_start": None if test.empty else test.date.min(),
    }
    if len(train) < min_train_orders or len(test) < min_test_orders:
        return result
    medians = train.groupby("side").arrival_execution_bp.median()
    predicted = test.side.map(medians)
    if predicted.isna().any():
        result["status"] = "unseen_test_side"
        return result
    error = test.arrival_execution_bp - predicted
    result.update(
        status="evaluated",
        baseline="training_side_median",
        baseline_test_mae_bp=float(error.abs().mean()),
        baseline_test_bias_bp=float(error.mean()),
        baseline_test_p90_absolute_error_bp=float(error.abs().quantile(0.9)),
    )
    if "predicted_arrival_bp" in test:
        mask = np.isfinite(test.predicted_arrival_bp)
        result["supplied_prediction_test_orders"] = int(mask.sum())
        if mask.any():
            err = test.loc[mask, "arrival_execution_bp"] - test.loc[mask, "predicted_arrival_bp"]
            result["supplied_prediction_test_mae_bp"] = float(err.abs().mean())
            result["supplied_predictions_ex_ante_verified"] = False
    return result


def public_calibration(frame, validation, *, min_group_orders=20):
    if min_group_orders < 20:
        raise ValueError("aggregate groups require at least twenty orders")
    _required(frame, ["data_kind", "side", "calibration_eligible"])
    if not frame.side.isin(["buy", "sell"]).all():
        raise ValueError("unreviewed side group")
    if not frame.data_kind.isin(KINDS).all():
        raise ValueError("invalid evidence kind")
    kinds = sorted(frame.data_kind.unique().tolist())
    result = {
        "schema_version": "ashare_execution_costs.order_calibration.public.v1",
        "data_kinds": kinds,
        "orders": len(frame),
        "eligible_orders": int(frame.calibration_eligible.sum()),
        "actual_order_calibrated": kinds == ["actual"] and validation.get("status") == "evaluated",
        "causal_own_impact_identified": False,
        "groups": [],
        "validation": {
            key: validation[key]
            for key in (
                "status",
                "train_orders",
                "purged_training_orders",
                "test_orders",
                "baseline",
                "baseline_test_mae_bp",
                "baseline_test_bias_bp",
                "baseline_test_p90_absolute_error_bp",
                "supplied_prediction_test_orders",
                "supplied_prediction_test_mae_bp",
                "supplied_predictions_ex_ante_verified",
            )
            if key in validation
        },
    }
    for side, group in frame.groupby("side"):
        if len(group) < min_group_orders:
            continue
        stats = {}
        for field in (
            "shortfall_bp",
            "arrival_execution_bp",
            "delay_bp",
            "market_adjusted_response_30s_bp",
            "market_adjusted_response_300s_bp",
            "market_adjusted_response_1800s_bp",
        ):
            if field not in group:
                continue
            values = group[field].dropna()
            if len(values) >= min_group_orders:
                stats[field] = {
                    "count": len(values),
                    "p50": float(values.median()),
                    "p90": float(values.quantile(0.9)),
                }
        result["groups"].append(
            {
                "side": side,
                "orders": len(group),
                "eligible_orders": int(group.calibration_eligible.sum()),
                "metrics": stats,
            }
        )
    return result
