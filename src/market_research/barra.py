from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .style_portfolios import analyze_tail_monotonicity, build_quantile_returns


def load_barra_summary(path: Path) -> dict[str, object]:
    root = Path(path)
    if not root.is_dir():
        raise FileNotFoundError(root)
    manifest = _read_json(root / "manifest.json")
    meta = _read_json(root / "meta.json")
    factor_summary = _read_json(root / "factor_summary.json")
    size = next((row for row in factor_summary if row.get("factor") == "size"), None)
    if size is None:
        raise ValueError("Barra result does not contain a size factor")
    return {
        "source_root": str(root),
        "schema_version": manifest.get("schema_version"),
        "generated_at": manifest.get("generated_at"),
        "factor_count": meta.get("factor_count", len(meta.get("factors", []))),
        "factors": meta.get("factors", []),
        "coverage_start": meta.get("data_start"),
        "coverage_end": meta.get("data_end"),
        "rebalance_frequency": meta.get("rebalance_frequency"),
        "quantiles": meta.get("quantiles"),
        "size_factor": size,
    }


def summarize_barra_factor_file(path: Path) -> dict[str, object]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    frame = pd.read_csv(source)
    if "trade_date" not in frame.columns or len(frame.columns) != 2:
        raise ValueError("factor daily file must contain trade_date and one factor column")
    factor = next(column for column in frame.columns if column != "trade_date")
    values = pd.to_numeric(frame[factor], errors="coerce")
    dates = pd.to_datetime(frame["trade_date"], errors="coerce")
    valid = values.notna() & dates.notna()
    if not valid.any():
        raise ValueError(f"factor file has no valid observations: {source}")
    return {
        "factor": factor.removeprefix("factor_").removesuffix("_daily"),
        "observations": int(valid.sum()),
        "coverage_start": dates.loc[valid].min().date().isoformat(),
        "coverage_end": dates.loc[valid].max().date().isoformat(),
        "mean_return": float(values.loc[valid].mean()),
    }


def analyze_size_monotonicity(
    panel: pd.DataFrame, quantiles: int = 10, holding_period: int = 1
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Size evidence with positive caps and shared formation/coverage semantics.

    Monotonicity expects returns to decrease as size grows. tail_spread retains
    the historical small-minus-large sign. Unavailable metrics are None.
    """
    required = {"symbol", "date", "adj_close", "market_cap"}
    missing = required.difference(panel.columns)
    if missing:
        raise ValueError("missing panel columns: " + ",".join(sorted(missing)))

    frame = panel.copy()
    caps = pd.to_numeric(frame["market_cap"], errors="coerce")
    frame["market_cap"] = caps.where(caps.gt(0))
    result = build_quantile_returns(frame, "market_cap", quantiles, holding_period)
    summary = analyze_tail_monotonicity(result, direction="descending")
    # Generic diagnostics use first-minus-last in the requested bucket order;
    # Barra has always reported small-minus-large, regardless of expected slope.
    if summary["tail_spread"] is not None:
        summary["tail_spread"] = -summary["tail_spread"]
    eligible_rows = int(result["count"].sum())
    observed_rows = int(result["observed_return_count"].sum())
    summary.update({
        "quantiles": int(quantiles),
        "holding_period": int(holding_period),
        "tail_spread_definition": "small_minus_large",
        "coverage_start": result["formation_date"].min().date().isoformat() if not result.empty else None,
        "coverage_end": result["formation_date"].max().date().isoformat() if not result.empty else None,
        "formation_dates": int(result["formation_date"].nunique()),
        "eligible_rows": eligible_rows,
        "excluded_rows": int(len(frame) - eligible_rows),
        "observed_return_count": observed_rows,
        "missing_return_count": eligible_rows - observed_rows,
        "return_coverage": observed_rows / eligible_rows if eligible_rows else None,
        "unavailable_target_rows": result.attrs["unavailable_target_rows"],
        "unavailable_target_dates": result.attrs["unavailable_target_dates"],
    })
    return result.sort_values(["bucket", "formation_date"]).reset_index(drop=True), summary


def _read_json(path: Path) -> dict[str, object] | list[dict[str, object]]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)
