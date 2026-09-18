from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


CLASSIFICATIONS = (
    "suspension_evidence",
    "st_event_evidence",
    "delist_evidence",
    "terminal_or_source_gap",
    "unclassified_gap",
)


def _date_series(frame: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_datetime(frame.get(column), format="mixed", errors="coerce").dt.date


def _code_series(frame: pd.DataFrame, column: str = "ts_code") -> pd.Series:
    return frame.get(column, pd.Series(index=frame.index, dtype="string")).astype("string").str.upper()


def _event_in_window(events: pd.DataFrame, code: str, start: Any, end: Any, date_columns: tuple[str, ...]) -> bool:
    if events is None or events.empty or pd.isna(start):
        return False
    rows = events.loc[_code_series(events).eq(code)].copy()
    if rows.empty:
        return False
    event_dates = pd.Series(pd.NaT, index=rows.index, dtype="datetime64[ns]")
    for column in date_columns:
        if column in rows:
            event_dates = event_dates.fillna(_date_series(rows, column))
    start_value = pd.Timestamp(start)
    valid = event_dates.notna() & event_dates.ge(start_value)
    if pd.notna(end):
        valid &= event_dates.le(pd.Timestamp(end))
    return bool(valid.any())


def classify_missing_holdings(
    missing: pd.DataFrame,
    instruments: pd.DataFrame | None = None,
    st_events: pd.DataFrame | None = None,
    suspend_events: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Classify only evidence in the confirmed missing-price window.

    The window starts at the expected next market date and ends immediately
    before the next observed quote. A missing terminal quote has no upper bound.
    Evidence is deliberately conservative: unresolved gaps stay unclassified.
    """
    if missing.empty:
        return missing.assign(classification=pd.Series(dtype="string"), evidence_date=pd.NaT)
    result = missing.copy()
    result["ts_code"] = _code_series(result)
    result["date"] = _date_series(result, "date")
    result["next_market_date"] = _date_series(result, "next_market_date")
    result["next_stock_date"] = _date_series(result, "next_stock_date")
    result["classification"] = "unclassified_gap"
    result["has_suspension_evidence"] = False
    result["has_st_event_evidence"] = False
    result["has_delist_evidence"] = False
    result["evidence_date"] = pd.Series([None] * len(result), index=result.index, dtype="object")
    instrument_dates: dict[str, Any] = {}
    if instruments is not None and not instruments.empty and "delist_date" in instruments:
        normalized = instruments.copy()
        normalized["ts_code"] = _code_series(normalized)
        normalized["delist_date"] = _date_series(normalized, "delist_date")
        instrument_dates = normalized.dropna(subset=["delist_date"]).set_index("ts_code")["delist_date"].to_dict()
    for index, row in result.iterrows():
        start = row["next_market_date"]
        end = row["next_stock_date"]
        if pd.isna(start):
            result.at[index, "classification"] = "terminal_or_source_gap"
            continue
        code = str(row["ts_code"])
        delist_date = instrument_dates.get(code)
        has_delist = delist_date is not None and delist_date >= start and (pd.isna(end) or delist_date <= end)
        has_suspend = _event_in_window(suspend_events, code, start, end, ("trade_date", "suspend_date"))
        has_st = _event_in_window(st_events, code, start, end, ("imp_date", "pub_date", "trade_date"))
        result.at[index, "has_delist_evidence"] = has_delist
        result.at[index, "has_suspension_evidence"] = has_suspend
        result.at[index, "has_st_event_evidence"] = has_st
        if has_delist:
            result.at[index, "classification"] = "delist_evidence"
            result.at[index, "evidence_date"] = delist_date
        elif has_suspend and has_st:
            result.at[index, "classification"] = "suspension_and_st_evidence"
        elif has_suspend:
            result.at[index, "classification"] = "suspension_evidence"
        elif has_st:
            result.at[index, "classification"] = "st_event_evidence"
        elif pd.isna(end):
            result.at[index, "classification"] = "terminal_or_source_gap"
    return result


@dataclass(frozen=True)
class RepairVariant:
    name: str
    observations: int
    coverage_start: str | None
    coverage_end: str | None
    final_nav: float | None
    cumulative_return: float | None
    max_drawdown: float | None


def _variant(name: str, returns: pd.Series, dates: pd.Series) -> RepairVariant:
    frame = pd.DataFrame({"date": dates, "return": returns}).dropna(subset=["return"])
    if frame.empty:
        return RepairVariant(name, 0, None, None, None, None, None)
    nav = (1 + frame["return"].astype(float)).cumprod()
    drawdown = nav / nav.cummax() - 1
    return RepairVariant(
        name=name,
        observations=int(len(frame)),
        coverage_start=str(frame["date"].iloc[0]),
        coverage_end=str(frame["date"].iloc[-1]),
        final_nav=float(nav.iloc[-1]),
        cumulative_return=float(nav.iloc[-1] - 1),
        max_drawdown=float(drawdown.min()),
    )


def summarize_repair_variants(result: pd.DataFrame, classified: pd.DataFrame) -> list[dict[str, Any]]:
    """Return strict, broad sensitivities, and evidence-only carry metrics."""
    frame = result.sort_values("date").copy()
    dates = frame["date"].astype(str)
    variants = [_variant("strict", frame["return"], dates), _variant("partial", frame["partial_return"], dates), _variant("carry_all_missing", frame["carry_return"], dates)]
    if classified.empty:
        evidence_return = frame["return"]
    else:
        counts = classified.groupby("date").agg(
            missing_count=("classification", "size"),
            suspension_count=("has_suspension_evidence", "sum"),
        )
        evidence_return = frame["return"].copy()
        for index, row in frame.iterrows():
            counts_row = counts.loc[row["date"]] if row["date"] in counts.index else None
            if counts_row is not None and counts_row["missing_count"] == counts_row["suspension_count"]:
                priced = int(row["priced_count"])
                selected = int(row["selected_count"])
                evidence_return.loc[index] = float(row["partial_return"]) * priced / selected if selected else float("nan")
    variants.append(asdict(_variant("carry_evidence_only", evidence_return, dates)))
    return [asdict(item) if isinstance(item, RepairVariant) else item for item in variants]


def load_parquet_frame(root: str | Path | None) -> pd.DataFrame:
    if not root:
        return pd.DataFrame()
    path = Path(root)
    if not path.exists():
        return pd.DataFrame()
    files = list(path.glob("**/*.parquet"))
    if not files:
        return pd.DataFrame()
    return pd.concat((pd.read_parquet(file) for file in files), ignore_index=True)


def load_missing_holdings_from_parquet(
    data_root: str | Path,
    constituent_count: int = 400,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    import duckdb

    root = Path(data_root)
    filters = ["trade_date IS NOT NULL", "adj_close > 0", "total_mv > 0"]
    parameters: list[object] = [str(root / "**" / "*.parquet"), constituent_count]
    if start_date:
        filters.append("trade_date >= CAST(? AS DATE)")
        parameters.insert(-1, start_date)
    if end_date:
        filters.append("trade_date <= CAST(? AS DATE)")
        parameters.insert(-1, end_date)
    query = f"""
        WITH raw AS (
            SELECT ts_code, trade_date, CAST(adj_close AS DOUBLE) AS adj_close,
                   CAST(total_mv AS DOUBLE) AS total_mv,
                   COALESCE(is_st, false) AS is_st,
                   COALESCE(is_suspended, false) AS is_suspended
            FROM (
                SELECT ts_code,
                       COALESCE(try_cast(trade_date AS DATE), try_strptime(trade_date, '%Y%m%d')) AS trade_date,
                       adj_close, total_mv, is_st, is_suspended
                FROM read_parquet(?, union_by_name=true)
            ) source
            WHERE {' AND '.join(filters)}
        ),
        dates AS (
            SELECT trade_date, LEAD(trade_date) OVER (ORDER BY trade_date) AS next_market_date
            FROM (SELECT DISTINCT trade_date FROM raw)
        ),
        prices AS (
            SELECT *, LEAD(trade_date) OVER (PARTITION BY ts_code ORDER BY trade_date) AS next_stock_date,
                   LEAD(adj_close) OVER (PARTITION BY ts_code ORDER BY trade_date) AS next_adj_close
            FROM raw
        ),
        ranked AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY trade_date ORDER BY total_mv, ts_code) AS rank
            FROM prices WHERE NOT is_st AND NOT is_suspended
        )
        SELECT ts_code, trade_date AS date, next_market_date, next_stock_date,
               next_adj_close, adj_close, total_mv
        FROM ranked JOIN dates USING (trade_date)
        WHERE rank <= ?
          AND next_market_date IS NOT NULL
          AND NOT (next_stock_date = next_market_date AND next_adj_close > 0)
        ORDER BY date, ts_code
    """
    connection = duckdb.connect()
    try:
        return connection.execute(query, parameters).fetchdf()
    finally:
        connection.close()
