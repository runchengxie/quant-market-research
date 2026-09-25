from __future__ import annotations

from numbers import Integral

import numpy as np
import pandas as pd


def build_quantile_returns(
    panel: pd.DataFrame,
    factor_column: str,
    quantiles: int = 10,
    holding_period: int = 1,
    date_column: str = "date",
    return_column: str = "adj_close",
) -> pd.DataFrame:
    """Build formation-based, equal-weight factor quantile returns.

    Order finite factors ascending, breaking ties by symbol; assign one-based
    ranks using ceil(rank * quantiles / n), evaluated with integer arithmetic.
    Sizes differ by at most one. If n < quantiles, some labels remain empty.
    Signed factors are valid; formation and target prices must be finite and
    positive. Eligibility flags apply only on the formation date.

    The target is holding_period dates ahead in the global input calendar;
    missing symbol quotes never move that target or change formation membership.
    Dates without a global target are omitted. count includes every formation
    member. Incomplete groups have null full-portfolio mean/median, with partial
    estimates exposed only as observed_only_* alongside return coverage.
    """
    if (
        not isinstance(quantiles, Integral) or isinstance(quantiles, bool) or quantiles < 2
        or not isinstance(holding_period, Integral) or isinstance(holding_period, bool)
        or holding_period < 1
    ):
        raise ValueError("quantiles must be an integer >= 2 and holding_period a positive integer")
    required = {"symbol", date_column, factor_column, return_column}
    missing = required.difference(panel.columns)
    if missing:
        raise ValueError("missing panel columns: " + ", ".join(sorted(missing)))
    if "market" in panel.columns and panel["market"].astype("string").str.lower().eq("a_share").any():
        eligibility = {"is_tradable", "is_st", "is_suspended"}
        absent = eligibility.difference(panel.columns)
        if absent:
            raise ValueError("A-share eligibility columns are required: " + ", ".join(sorted(absent)))

    # Internal names keep custom input columns independent of derived fields.
    frame = pd.DataFrame({
        "symbol": panel["symbol"].astype("string"),
        "date": pd.to_datetime(panel[date_column], errors="coerce"),
        "factor": pd.to_numeric(panel[factor_column], errors="coerce").astype(float),
        "price": pd.to_numeric(panel[return_column], errors="coerce").astype(float),
    })
    if frame.duplicated(["symbol", "date"]).any():
        raise ValueError("duplicate symbol/date rows in panel")
    for column, default in (("is_tradable", True), ("is_st", False), ("is_suspended", False)):
        # Null flags are ineligible; non-A-share generic panels may omit flags.
        frame[column] = (
            panel[column].fillna(column != "is_tradable").astype(bool)
            if column in panel else default
        )

    dates = sorted(frame["date"].dropna().unique())
    targets = {
        date: dates[i + holding_period]
        for i, date in enumerate(dates[:-holding_period])
    }
    frame["target_date"] = pd.to_datetime(frame["date"].map(targets))
    formation_mask = (
        frame["date"].notna()
        & frame["symbol"].notna() & frame["symbol"].str.strip().ne("")
        & np.isfinite(frame["factor"])
        & np.isfinite(frame["price"]) & frame["price"].gt(0)
        & frame["is_tradable"] & ~frame["is_st"] & ~frame["is_suspended"]
    )
    eligible = frame.loc[formation_mask & frame["target_date"].notna()].copy()
    eligible = eligible.sort_values(["date", "factor", "symbol"], kind="stable")
    groups = eligible.groupby("date")
    rank = groups.cumcount() + 1
    size = groups["symbol"].transform("size")
    eligible["bucket"] = ((rank * quantiles + size - 1) // size).astype(int)

    quotes = frame[["symbol", "date", "price"]].rename(
        columns={"date": "target_date", "price": "target_price"}
    )
    eligible = eligible.merge(quotes, on=["symbol", "target_date"], how="left", validate="many_to_one")
    target_price = eligible["target_price"].where(
        np.isfinite(eligible["target_price"]) & eligible["target_price"].gt(0)
    )
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        forward_return = target_price / eligible["price"] - 1.0
    eligible["forward_return"] = forward_return.where(np.isfinite(forward_return))

    result = (
        eligible.groupby(["date", "bucket"], as_index=False)
        .agg(
            mean_forward_return=("forward_return", "mean"),
            median_forward_return=("forward_return", "median"),
            count=("forward_return", "size"),
            observed_return_count=("forward_return", "count"),
            target_date=("target_date", "first"),
        )
        .rename(columns={"date": "formation_date"})
    )
    result["bucket_label"] = result["bucket"].map(lambda value: f"Q{value}")
    result["missing_return_count"] = result["count"] - result["observed_return_count"]
    result["return_coverage"] = result["observed_return_count"] / result["count"]
    for statistic in ("mean", "median"):
        column = f"{statistic}_forward_return"
        result[column] = result[column].where(np.isfinite(result[column]))
        result[f"observed_only_{column}"] = result[column]
        result[column] = result[column].where(result["missing_return_count"].eq(0))
    result["requested_quantiles"] = int(quantiles)
    # Preserve the existing CSV column prefix for downstream readers.
    original_columns = [
        "formation_date", "bucket", "mean_forward_return", "median_forward_return",
        "count", "bucket_label",
    ]
    result = result[original_columns + [c for c in result if c not in original_columns]]
    result = result.sort_values(["formation_date", "bucket"]).reset_index(drop=True)
    result.attrs["unavailable_target_rows"] = int(
        (formation_mask & frame["target_date"].isna()).sum()
    )
    result.attrs["unavailable_target_dates"] = int(
        frame.loc[frame["target_date"].isna(), "date"].nunique()
    )
    return result
