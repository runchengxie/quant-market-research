from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from ..contracts import PanelMetadata, normalize_panel


def build_a_share_panel(
    data_root: Path,
    as_of: str | None = None,
    fx_rate: float | None = None,
    use_duckdb: bool = False,
    *,
    retain_ineligible_quotes: bool = False,
) -> tuple[pd.DataFrame, PanelMetadata]:
    """Load formation-eligible rows, optionally retaining holding-date quotes.

    Retention keeps all dated observations without inventing or filling prices.
    is_tradable records formation eligibility: finite positive amount/cap and
    known non-ST/non-suspended status. Unknown status remains null in its flag
    and never grants eligibility. Holding-price consumers may still use genuine
    quotes from rows that are ineligible for a new formation.
    """
    root = Path(data_root)
    dated_st_source = _has_dated_st_source(root)
    if not dated_st_source and not retain_ineligible_quotes:
        raise ValueError("A-share formation requires validated dated ST history in manifest.yml")
    if use_duckdb and root.is_dir():
        return _build_a_share_with_duckdb(
            root, as_of, fx_rate, retain_ineligible_quotes, dated_st_source
        )
    rows: list[pd.DataFrame] = []
    sources = [root] if root.is_file() else sorted(root.rglob("*.parquet"))
    for source in sources:
        frame = pd.read_parquet(source)
        prepared = _prepare_quotes(
            frame, str(source), source.stem, as_of, retain_ineligible_quotes, dated_st_source
        )
        if not prepared.empty:
            rows.append(prepared)
    panel = pd.concat(rows, ignore_index=True) if rows else _empty_panel()
    metadata = _metadata(
        panel, "Tushare A-share daily-clean", as_of, "CNY", fx_rate,
        retain_ineligible_quotes, dated_st_source,
    )
    return normalize_panel(panel, metadata)


def _build_a_share_with_duckdb(
    root: Path, as_of: str | None, fx_rate: float | None,
    retain_ineligible_quotes: bool, dated_st_source: bool,
) -> tuple[pd.DataFrame, PanelMetadata]:
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("DuckDB is required for use_duckdb=True") from exc
    pattern = str(root / "**" / "*.parquet")
    query = """
        SELECT filename,
               COLUMNS('^(ts_code|trade_date|close|adj_close|vol|amount|total_mv|is_st|is_suspended)$')
        FROM read_parquet(?, union_by_name=true, filename=true)
    """
    with duckdb.connect() as connection:
        frame = connection.execute(query, [pattern]).fetchdf()
    fallback_symbols = frame["filename"].map(lambda filename: Path(filename).stem)
    panel = _prepare_quotes(
        frame, str(root), fallback_symbols, as_of, retain_ineligible_quotes,
        dated_st_source,
    )
    metadata = _metadata(
        panel, "Tushare A-share daily-clean DuckDB scan", as_of, "CNY", fx_rate,
        retain_ineligible_quotes, dated_st_source,
    )
    return normalize_panel(panel, metadata)


def _prepare_quotes(
    frame: pd.DataFrame,
    source: str,
    fallback_symbols: str | pd.Series,
    as_of: str | None,
    retain_ineligible_quotes: bool,
    dated_st_source: bool,
) -> pd.DataFrame:
    if "trade_date" not in frame:
        return _empty_panel()
    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["trade_date"], errors="coerce").dt.date
    for column in ("amount", "total_mv", "close", "adj_close", "vol"):
        values = frame.get(column, pd.Series(np.nan, index=frame.index))
        frame[column] = pd.to_numeric(values, errors="coerce").astype(float)
    for column in ("is_st", "is_suspended"):
        values = frame.get(column, pd.Series(pd.NA, index=frame.index))
        frame[column] = values.astype("string").str.strip().str.lower().map({
            "true": True, "false": False, "1": True, "0": False,
            "1.0": True, "0.0": False,
        }).astype("boolean")
    if not dated_st_source:
        frame["is_st"] = pd.Series(pd.NA, index=frame.index, dtype="boolean")
    symbols = frame.get("ts_code", pd.Series(pd.NA, index=frame.index)).astype("string")
    symbols = symbols.str.strip()
    frame["symbol"] = symbols.where(symbols.notna() & symbols.ne(""), fallback_symbols)
    frame["is_tradable"] = (
        np.isfinite(frame["amount"]) & frame["amount"].gt(0)
        & np.isfinite(frame["total_mv"]) & frame["total_mv"].gt(0)
        & frame["is_st"].eq(False) & frame["is_suspended"].eq(False)
    ).fillna(False).astype(bool)
    selected = frame["date"].notna()
    if as_of is not None:
        selected &= frame["date"] <= pd.Timestamp(as_of).date()
    if not retain_ineligible_quotes:
        selected &= frame["is_tradable"]
    eligible = frame.loc[selected]
    return pd.DataFrame(
        {
            "market": "a_share",
            "symbol": eligible["symbol"],
            "date": eligible["date"],
            "close": eligible["close"],
            "adj_close": eligible["adj_close"],
            "volume": eligible["vol"],
            "turnover": eligible["amount"] * 1_000,
            "market_cap": eligible["total_mv"] * 10_000,
            "currency": "CNY",
            "is_tradable": eligible["is_tradable"],
            "is_st": eligible["is_st"],
            "is_suspended": eligible["is_suspended"],
            "source": source,
        }
    )


def _empty_panel() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "market", "symbol", "date", "close", "adj_close", "volume", "turnover", "market_cap",
            "currency", "is_tradable", "is_st", "is_suspended", "source",
        ]
    )


def _has_dated_st_source(root: Path) -> bool:
    directory = root.parent if root.is_file() else root
    for candidate in (directory / "manifest.yml", directory.parent / "manifest.yml"):
        if not candidate.is_file():
            continue
        manifest = yaml.safe_load(candidate.read_text(encoding="utf-8"))
        if isinstance(manifest, dict):
            inputs = manifest.get("inputs")
            return isinstance(inputs, dict) and bool(inputs.get("st_history_file"))
    return False


def _metadata(
    panel: pd.DataFrame, source: str, as_of: str | None, currency: str,
    fx_rate: float | None, retain_ineligible_quotes: bool = False,
    dated_st_source: bool = False,
) -> PanelMetadata:
    start = str(panel["date"].min()) if not panel.empty else None
    end = str(panel["date"].max()) if not panel.empty else None
    quality_status = "verified" if not panel.empty and dated_st_source else "incomplete"
    if retain_ineligible_quotes:
        # Retaining quotes is not source validation. Known ineligible holding
        # rows are fine, but unknown eligibility evidence must remain visible.
        eligibility_known = (
            not panel.empty
            and panel[["is_st", "is_suspended"]].notna().to_numpy().all()
            and np.isfinite(panel[["turnover", "market_cap"]].to_numpy()).all()
        )
        quality_status = (
            "derived" if dated_st_source and eligibility_known and panel["is_tradable"].any()
            else "incomplete"
        )
    return PanelMetadata(
        source=source,
        as_of=as_of or end or "",
        currency=currency,
        universe_filter=(
            "all dated quotes retained for holding marks; formation eligibility: "
            "finite positive amount/market cap; known non-ST/non-suspended"
            if retain_ineligible_quotes else "positive amount/market cap; non-ST; non-suspended"
        ),
        fx_method="native currency" if fx_rate is None else f"reference FX rate {fx_rate:g}",
        feature_lag=1,
        coverage_start=start,
        coverage_end=end,
        calendar_mode="observed_daily",
        quality_status=quality_status,
    )
