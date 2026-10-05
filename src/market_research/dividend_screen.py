"""Offline dividend research calculations; monetary units must be consistent."""

import math

import pandas as pd


def _dates(values):
    return pd.to_datetime(values.astype("string"), errors="coerce", format="mixed")


def dividend_totals(events: pd.DataFrame, basis: str = "implementation") -> pd.DataFrame:
    """Aggregate implemented tax-inclusive DPS; conflicting event versions fail closed.

    Event key: security, fiscal period and ex-date. cash_amount, when supplied,
    must already be in the same currency/unit as annual parent net profit.
    """
    if basis not in {"implementation", "fiscal"}:
        raise ValueError("basis must be implementation or fiscal")
    df = events.loc[events.div_proc.isin(["实施", "implemented"])].copy()
    keys = ["ts_code", "end_date", "ex_date"]
    df["ex_date"] = _dates(df.ex_date)
    df["end_date"] = _dates(df.end_date)
    if df[keys].isna().any().any():
        raise ValueError("implemented dividend missing security, fiscal date or ex-date")
    amounts = ["cash_div_tax"] + (["cash_amount"] if "cash_amount" in df else [])
    for field in amounts:
        df[field] = pd.to_numeric(df[field], errors="coerce")
        if (df[field].dropna() < 0).any():
            raise ValueError("negative dividend")
        if df.groupby(keys)[field].nunique(dropna=False).gt(1).any():
            raise ValueError(f"conflicting dividend event: {field}")
    df = df.drop_duplicates(keys)
    df["year"] = df["ex_date" if basis == "implementation" else "end_date"].dt.year
    # A missing amount in any installment must not produce a partial total.
    return df.groupby(["ts_code", "year"], as_index=False)[amounts].agg(
        lambda values: values.sum() if values.notna().all() else float("nan")
    )


def screen(
    totals: pd.DataFrame, year_end_quotes: pd.DataFrame, threshold_pct: float = 5.0
) -> pd.DataFrame:
    """Quotes are explicitly supplied final market-session closes, unadjusted."""
    result = year_end_quotes.merge(
        totals, on=["ts_code", "year"], how="left", validate="one_to_one"
    )
    result["yield_pct"] = result.cash_div_tax.div(result.close.where(result.close > 0)) * 100
    result["selected"] = result.yield_pct.gt(threshold_pct)
    return result


def annual_volatility(prices: pd.DataFrame, years, minimum_returns: int = 200):
    """Sample standard deviation of adjusted daily simple returns, annualized by sqrt(252).

    Include the preceding observed session to compute January's first return.
    Missing prices break both adjacent returns; no forward filling is performed.
    """
    df = prices.copy()
    df["trade_date"] = _dates(df.trade_date)
    if df[["ts_code", "trade_date"]].isna().any().any():
        raise ValueError("missing price key")
    if df.duplicated(["ts_code", "trade_date"]).any():
        raise ValueError("duplicate daily price")
    rows = []
    for code, group in df.groupby("ts_code"):
        group = group.sort_values("trade_date")
        price = pd.to_numeric(group.adj_close, errors="coerce")
        returns = price.where(price > 0).pct_change(fill_method=None)
        for year in years:
            sample = returns.loc[group.trade_date.dt.year.eq(year)].dropna()
            count = len(sample)
            rows.append(
                {
                    "ts_code": code,
                    "year": year,
                    "return_count": count,
                    "volatility_pct": sample.std(ddof=1) * math.sqrt(252) * 100,
                    "sample_status": "sufficient"
                    if count >= minimum_returns
                    else "insufficient_sample",
                }
            )
    return pd.DataFrame(
        rows, columns=["ts_code", "year", "return_count", "volatility_pct", "sample_status"]
    )


def head_flags(universe: pd.DataFrame):
    """Year-end A-share quote total market-cap proxy, SW L1 and brokers separately.

    Input must contain the full A-share universe; H-share lines should receive their
    issuer's A-share flags through an explicit issuer mapping after this calculation.
    """
    df = universe.copy()
    if df.duplicated(["ts_code", "year"]).any():
        raise ValueError("duplicate issuer year")
    ordered = df.sort_values(["total_mv", "ts_code"], ascending=[False, True])
    valid = ordered.total_mv.notna() & ordered.total_mv.gt(0) & ordered.sw_l1.notna()
    rank = ordered.loc[valid].groupby(["year", "sw_l1"]).cumcount() + 1
    df["industry_head"] = df.index.isin(rank.index[rank.le(3)])
    brokers = ordered.loc[ordered.is_broker.eq(True) & ordered.total_mv.gt(0)]
    broker_rank = brokers.groupby("year").cumcount() + 1
    df["broker_head"] = df.index.isin(broker_rank.index[broker_rank.le(3)])
    return df


def payout_ratios(fiscal: pd.DataFrame):
    """Fiscal DPS and cash amount must match the profit's fiscal year, never ex-year."""
    df = fiscal.copy()
    for field in ["cash_amount", "net_profit_parent", "eps"]:
        if field not in df:
            df[field] = float("nan")
    amount_valid = df.cash_amount.notna() & df.net_profit_parent.gt(0)
    proxy_valid = df.cash_div_tax.notna() & df.eps.gt(0)
    df["payout_pct"] = df.cash_amount.div(df.net_profit_parent.where(amount_valid)) * 100
    df["payout_method"] = pd.Series("unavailable", index=df.index)
    df.loc[amount_valid, "payout_method"] = "cash_amount/net_profit_parent"
    fallback = ~amount_valid & proxy_valid
    df.loc[fallback, "payout_pct"] = (
        df.loc[fallback, "cash_div_tax"] / df.loc[fallback, "eps"] * 100
    )
    df.loc[fallback, "payout_method"] = "dps/eps_proxy"
    return df


def normalize_tushare_cash(events: pd.DataFrame):
    """Tushare base_share is ten thousand shares; output cash_amount is yuan."""
    df = events.copy()
    base = pd.to_numeric(df.base_share, errors="coerce")
    dps = pd.to_numeric(df.cash_div_tax, errors="coerce")
    df["cash_amount"] = base.where(base > 0) * 10000 * dps
    return df


def restated_dividend_events(events: pd.DataFrame):
    """Restate implemented calendar-year DPS to that year's ending share basis.

    Call on implemented events, including pure stock distributions. A distribution
    applies to its own day's cash and every earlier cash payment that same year.
    Financing issuance is not a stock split and must not enter stk_div.
    """
    df = events.copy()
    dates = _dates(df.ex_date)
    if dates.isna().any() or df.ts_code.isna().any():
        raise ValueError("missing security or ex-date")
    stock = pd.to_numeric(
        df.get("stk_div", pd.Series(float("nan"), index=df.index)), errors="coerce"
    )
    if stock.dropna().lt(0).any():
        raise ValueError("negative stock distribution")
    df["stk_div_assumed_zero"] = stock.isna()
    df["cash_div_tax_raw"] = pd.to_numeric(df.cash_div_tax, errors="coerce")
    actions = pd.DataFrame(
        {"ts_code": df.ts_code, "ex_date": dates, "year": dates.dt.year, "stk_div": stock.fillna(0)}
    )
    # Separate zero-stock cash records do not create another stock action.
    positive = actions.loc[actions.stk_div.gt(0)]
    if positive.groupby(["ts_code", "ex_date"]).stk_div.nunique().gt(1).any():
        raise ValueError("conflicting same-day stock distribution")
    actions = actions.groupby(["ts_code", "year", "ex_date"], as_index=False).stk_div.max()
    actions = actions.sort_values("ex_date", ascending=False)
    actions["share_factor_to_year_end"] = (
        (1 + actions.stk_div).groupby([actions.ts_code, actions.year]).cumprod()
    )
    keys = pd.DataFrame({"ts_code": df.ts_code, "year": dates.dt.year, "ex_date": dates})
    factors = keys.merge(
        actions, on=["ts_code", "year", "ex_date"], how="left", validate="many_to_one"
    )
    df["share_factor_to_year_end"] = factors.share_factor_to_year_end.to_numpy()
    df["cash_div_tax"] = df.cash_div_tax_raw / df.share_factor_to_year_end
    return df
