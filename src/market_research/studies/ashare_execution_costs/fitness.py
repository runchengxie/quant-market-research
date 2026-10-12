"""Bounded source-selection and event-key checks, not vendor-semantic validation."""

from __future__ import annotations

import pandas as pd


def reconcile_selection(expected: pd.DataFrame, saved: pd.DataFrame) -> dict:
    keys = ["SecuCode", "minute"]
    for rows in (expected, saved):
        if rows[keys].isna().any().any() or rows.duplicated(keys).any():
            raise ValueError("null or duplicate selection keys")
    joined = expected.merge(
        saved,
        on=keys,
        how="outer",
        suffixes=("_raw", "_saved"),
        indicator=True,
        validate="one_to_one",
    )
    both = joined._merge.eq("both")
    match = (
        both
        & joined.absolute_ms_raw.eq(joined.absolute_ms_saved)
        & joined.source_row_raw.eq(joined.source_row_saved)
    )
    return {
        "expected_bins": len(expected),
        "saved_bins": len(saved),
        "missing_saved_bins": int(joined._merge.eq("left_only").sum()),
        "extra_saved_bins": int(joined._merge.eq("right_only").sum()),
        "wrong_earliest_bins": int((both & ~match).sum()),
        "matched_bins": int(match.sum()),
    }


def reference_timing(con, order_view: str, trade_view: str, candidate: str) -> dict:
    """Candidate presence, ambiguity and first availability; no side/cancel meaning."""
    for name in (order_view, trade_view, candidate):
        if not name.replace("_", "").isalnum():
            raise ValueError("simple SQL identifiers required")
    columns = [
        {row[0] for row in con.execute(f"DESCRIBE {name}").fetchall()}
        for name in (order_view, trade_view)
    ]
    keys = ["SecuCode"] + (["Channel"] if all("Channel" in c for c in columns) else [])
    group = ",".join(keys)
    result = {
        "candidate": candidate,
        "scope": "security_channel" if len(keys) > 1 else "security_only",
    }
    for side, ref in (("buy", "BuyID"), ("sell", "SellID")):
        join = " AND ".join(f"t.{k}=o.{k}" for k in keys) + f" AND t.{ref}=o.order_key"
        row = (
            con.execute(f"""WITH o AS (
          SELECT {group},{candidate} order_key,count(*) n,min(time_ms_absolute) first_ms
          FROM {order_view} WHERE {candidate}>0 GROUP BY {group},{candidate})
          SELECT count(*) eligible_trades,
            count_if(o.n=1 AND o.first_ms<=t.time_ms_absolute) unique_key_available_by_trade,
            count_if(o.n>1 AND o.first_ms<=t.time_ms_absolute) ambiguous_key_available_by_trade,
            count_if(o.first_ms>t.time_ms_absolute) key_only_after_trade,
            count_if(o.first_ms=t.time_ms_absolute) first_timestamp_equal_trade,
            count_if(o.order_key IS NULL) missing_key,
            count_if(t.{ref} IS NULL OR t.{ref}<=0) nonpositive_reference,
            count_if(o.order_key IS NOT NULL AND (o.first_ms IS NULL OR t.time_ms_absolute IS NULL)) unknown_clock
          FROM {trade_view} t LEFT JOIN o ON {join}
          WHERE t.Price>0 AND t.Volume>0""")
            .df()
            .iloc[0]
            .to_dict()
        )
        result[side] = {k: 0 if pd.isna(v) else int(v) for k, v in row.items()}
    return result


def prepare_paths(frame: pd.DataFrame, day: int, securities, *, max_arrival_delay_ms=60000):
    """Use only declared day; retain one raw quote per timestamp within fixed opening window."""
    eligible = frame.loc[
        frame.TradingDay.eq(day)
        & frame.SecuCode.isin(securities)
        & frame.time_ms.between(0, 300000)
    ].copy()
    paths = {}
    late = 0
    invalid = 0
    missing = 0
    for code in sorted(securities):
        path = (
            eligible.loc[eligible.SecuCode.eq(code)]
            .sort_values(["time_ms", "source_row"])
            .drop_duplicates("time_ms", keep="first")
        )
        if path.empty:
            missing += 1
        elif path.iloc[0].time_ms > max_arrival_delay_ms:
            late += 1
        elif "book_valid" in path and not path.book_valid.fillna(False).all():
            invalid += 1
        else:
            paths[int(code)] = path
    return paths, {
        "requested_securities": len(securities),
        "included_securities": len(paths),
        "missing_opening_securities": missing,
        "late_arrival_securities": late,
        "invalid_book_securities": invalid,
        "max_arrival_delay_ms": max_arrival_delay_ms,
    }
