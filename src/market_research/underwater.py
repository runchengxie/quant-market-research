from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


EPISODE_COLUMNS = (
    "peak_date",
    "underwater_start_date",
    "trough_date",
    "recovery_date",
    "underwater_trading_sessions",
    "peak_to_recovery_trading_sessions",
    "peak_to_last_observed_trading_sessions",
    "max_drawdown",
    "right_censored",
)


def _validated_nav(nav: pd.DataFrame) -> pd.DataFrame:
    if not {"date", "nav"}.issubset(nav.columns):
        raise ValueError("input must contain date and nav columns")
    frame = nav[["date", "nav"]].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["nav"] = pd.to_numeric(frame["nav"], errors="coerce")
    if frame.empty:
        raise ValueError("input contains no valid NAV records")
    if frame["date"].isna().any() or frame["nav"].isna().any():
        raise ValueError("date and nav values must be finite and non-null")
    if not np.isfinite(frame["nav"]).all() or frame["nav"].lt(0).any() or frame["nav"].iloc[0] <= 0:
        raise ValueError("NAV values must be finite and nonnegative, with a positive initial value")
    if frame["date"].duplicated().any():
        raise ValueError("NAV dates must be unique dates")
    return frame.sort_values("date", kind="stable").reset_index(drop=True)


def build_underwater_episodes(nav: pd.DataFrame) -> pd.DataFrame:
    """Describe each peak-to-recovery episode, retaining an open tail as censored.

    ``underwater_trading_sessions`` counts only observations below the prior
    high-water mark. ``peak_to_recovery_trading_sessions`` counts calendar-index
    steps from the peak observation to the first recovery observation.
    """
    frame = _validated_nav(nav)
    values = frame["nav"].to_numpy(dtype=float)
    dates = frame["date"].to_numpy()
    rows: list[dict[str, object]] = []
    peak_value = values[0]
    peak_position = 0
    active: dict[str, object] | None = None

    for position in range(1, len(frame)):
        value = values[position]
        if value >= peak_value:
            if active is not None:
                active["recovery_date"] = dates[position]
                active["peak_to_recovery_trading_sessions"] = position - peak_position
                active["right_censored"] = False
                rows.append(active)
                active = None
            peak_value = value
            peak_position = position
            continue

        drawdown = value / peak_value - 1.0
        if active is None:
            active = {
                "peak_date": dates[peak_position],
                "underwater_start_date": dates[position],
                "trough_date": dates[position],
                "recovery_date": pd.NaT,
                "underwater_trading_sessions": 1,
                "peak_to_recovery_trading_sessions": pd.NA,
                "peak_to_last_observed_trading_sessions": position - peak_position,
                "max_drawdown": drawdown,
                "right_censored": True,
            }
        else:
            active["underwater_trading_sessions"] = int(active["underwater_trading_sessions"]) + 1
            active["peak_to_last_observed_trading_sessions"] = position - peak_position
            if drawdown < float(active["max_drawdown"]):
                active["trough_date"] = dates[position]
                active["max_drawdown"] = drawdown

    if active is not None:
        rows.append(active)
    result = pd.DataFrame(rows, columns=EPISODE_COLUMNS)
    if not result.empty:
        result["underwater_trading_sessions"] = result["underwater_trading_sessions"].astype(int)
        result["right_censored"] = result["right_censored"].astype(bool)
        result["max_drawdown"] = result["max_drawdown"].astype(float)
    return result


def _survival_probability(episodes: pd.DataFrame, threshold: int) -> float:
    durations = episodes["underwater_trading_sessions"].astype(int)
    censored = episodes["right_censored"].astype(bool)
    survival = 1.0
    for time in sorted(set(durations.loc[~censored].tolist())):
        if time > threshold:
            break
        at_risk = int(durations.ge(time).sum())
        events = int((durations.eq(time) & ~censored).sum())
        if at_risk:
            survival *= 1.0 - events / at_risk
    return float(survival)


def summarize_underwater(
    episodes: pd.DataFrame,
    *,
    thresholds: Iterable[int] = (252, 504, 756, 1260),
) -> dict[str, object]:
    """Summarize completed durations and Kaplan–Meier survival past thresholds."""
    missing = set(EPISODE_COLUMNS).difference(episodes.columns)
    if missing:
        raise ValueError("underwater episodes are missing columns: " + ", ".join(sorted(missing)))
    if any(int(value) <= 0 for value in thresholds):
        raise ValueError("duration thresholds must be positive trading-session counts")

    if episodes.empty:
        return {
            "episode_count": 0,
            "completed_episode_count": 0,
            "right_censored_episode_count": 0,
            "max_drawdown": 0.0,
            "longest_completed_underwater_trading_sessions": None,
            "longest_observed_underwater_trading_sessions": None,
            "completed_duration_quantiles": {str(q): None for q in (0.5, 0.75, 0.9, 0.95)},
            "survival_probability_beyond_sessions": {str(int(t)): 1.0 for t in thresholds},
        }

    completed = episodes.loc[~episodes["right_censored"].astype(bool)]
    durations = completed["underwater_trading_sessions"].astype(int)
    all_durations = episodes["underwater_trading_sessions"].astype(int)
    quantiles = durations.quantile([0.5, 0.75, 0.9, 0.95]) if not durations.empty else None
    return {
        "episode_count": int(len(episodes)),
        "completed_episode_count": int(len(completed)),
        "right_censored_episode_count": int(episodes["right_censored"].astype(bool).sum()),
        "max_drawdown": float(episodes["max_drawdown"].min()),
        "longest_completed_underwater_trading_sessions": int(durations.max()) if not durations.empty else None,
        "longest_observed_underwater_trading_sessions": int(all_durations.max()),
        "completed_duration_quantiles": (
            {str(q): float(quantiles.loc[q]) for q in (0.5, 0.75, 0.9, 0.95)}
            if quantiles is not None
            else {str(q): None for q in (0.5, 0.75, 0.9, 0.95)}
        ),
        "survival_probability_beyond_sessions": {
            str(int(t)): _survival_probability(episodes, int(t)) for t in thresholds
        },
    }
