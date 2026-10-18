"""Calendar assumptions for daily bars; these are not retrieval-time vintages."""
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd


def load_daily(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"trade_date": str})
    if frame.empty:
        raise ValueError(f"Empty input: {path.name}")
    frame["date"] = pd.to_datetime(frame.trade_date, format="%Y%m%d", errors="raise")
    if frame.date.duplicated().any():
        raise ValueError(f"Duplicate dates: {path.name}")
    return frame.sort_values("date").reset_index(drop=True)


def assumed_available(date: pd.Timestamp, market: str) -> pd.Timestamp:
    """Conservative regular close plus 60 minutes; FX closes at GMT midnight.

    Regular US closes also conservatively cover earlier half-day closes.
    Asian schedules are used only to establish when a supplied bar could end;
    this does not independently establish exchange calendar completeness.
    """
    day = date.date()
    if market == "fx":
        close = datetime.combine(day + timedelta(days=1), time(), ZoneInfo("UTC"))
    else:
        hour, minute, zone = {
            "hsi": (16, 10, "Asia/Hong_Kong"),
            "n225": (15, 30 if str(day) >= "2024-11-05" else 0, "Asia/Tokyo"),
            # A conservative later regular close also bounds the older 15:00 close.
            "ks11": (15, 30, "Asia/Seoul"),
            "spx": (16, 0, "America/New_York"),
            "domestic": (15, 0, "Asia/Shanghai"),
        }[market]
        close = datetime.combine(day, time(hour, minute), ZoneInfo(zone))
    return pd.Timestamp(close + timedelta(hours=1)).tz_convert("UTC")


def cutoffs(dates: pd.Series) -> pd.Series:
    return (dates.dt.tz_localize("Asia/Shanghai") + pd.Timedelta(hours=8, minutes=45)
            ).dt.tz_convert("UTC")


def align_external(target: pd.DataFrame, sources: dict, lag: int = 0):
    """Join only completed bars, then measure new information since prior cutoff.

    Price changes between selected closes accumulate during A-share holidays;
    repeatedly selected foreign holiday bars produce zero new return.
    """
    out = target.copy()
    out["decision_utc"] = cutoffs(out.date)
    audits = []
    for name, (data, market, price) in sources.items():
        source = data[["date", price]].copy().rename(columns={price: "source_price"})
        source["available_utc"] = source.date.map(lambda d: assumed_available(d, market))
        matched = pd.merge_asof(
            out[["decision_utc"]], source.sort_values("available_utc"),
            left_on="decision_utc", right_on="available_utc", direction="backward",
        )
        for column in ["date", "source_price", "available_utc"]:
            matched[column] = matched[column].shift(lag)
        age = (out.decision_utc - matched.available_utc).dt.total_seconds() / 86400
        bad = (matched.available_utc > out.decision_utc).sum()
        if bad:
            raise ValueError("Input availability exceeds decision cutoff")
        stale = age > 10
        out[name] = matched.source_price.pct_change(fill_method=None).where(~stale)
        audits.append(pd.DataFrame({
            "target_date": out.date, "source": name, "source_date": matched.date,
            "assumed_available_utc": matched.available_utc, "decision_utc": out.decision_utc,
            "age_days": age, "stale": stale,
            "historical_retrieval_verified": False,
        }))
    return out, pd.concat(audits, ignore_index=True)


def validate_prices(data: pd.DataFrame, columns: list[str]) -> None:
    if not np.isfinite(data[columns].to_numpy(float)).all() or (data[columns] <= 0).any().any():
        raise ValueError("Missing, non-finite, or non-positive price")
