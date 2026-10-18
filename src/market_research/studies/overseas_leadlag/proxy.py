"""T+1-compatible daily-open ETF proxy with turnover cost sensitivities.

This statistical proxy is not an exchange matching engine or a fill replay.
"""
import numpy as np


def adjusted_etf(bars, factors):
    frame = bars.merge(factors[["date", "adj_factor"]], on="date", how="left",
                       validate="one_to_one")
    if frame.adj_factor.isna().any() or (frame.adj_factor <= 0).any():
        raise ValueError("Missing or invalid adjustment factors; no forward-fill")
    frame["adjusted_open"] = frame.open * frame.adj_factor
    frame["adjusted_close"] = frame.close * frame.adj_factor
    # A split must not look like a price-limit drop against an old nominal close.
    changed = frame.adj_factor.ne(frame.adj_factor.shift()) & frame.adj_factor.shift().notna()
    reference = frame.adjusted_close.shift() / frame.adj_factor
    frame["auction_reference"] = reference.where(changed, frame.pre_close)
    frame["adv20_yuan"] = (frame.amount * 1000).rolling(20).mean().shift(1)
    return frame


def simulate(frame, prediction, one_way_bp, budget=1e6, participation=.01):
    """Each row spans today's open to the next open; retain held exposures.

    Daily positions are either long or cash. Consecutive long signals retain
    the original holding, avoiding fictitious round-trip fees. A newly bought
    ETF cannot be sold before the next session. Guards use previous ADV and
    the auction opening price, never the later daily high/low or volume.
    """
    w = 0
    records = []
    for row in frame.itertuples(index=False):
        desired = int(prediction.get(row.date, -np.inf) > 0)
        reference = getattr(row, "auction_reference", row.pre_close)
        buy_locked = row.open / reference >= 1.099
        sell_locked = row.open / reference <= .901
        admitted = (np.isfinite(row.adv20_yuan) and row.adv20_yuan > 0
                    and budget <= row.adv20_yuan * participation)
        blocked = bool((desired > w and (buy_locked or not admitted))
                       or (desired < w and sell_locked))
        new_w = w if blocked else desired
        turnover = abs(new_w - w)
        gross = new_w * row.y
        cost = turnover * one_way_bp / 1e4
        records.append((row.date, new_w, turnover, gross - cost, blocked))
        w = new_w
    if not records:
        raise ValueError("Empty ETF simulation")
    # The final label ends at the NEXT open; liquidation is charged there.
    final_locked = float(frame.iloc[-1].exit_raw_open / frame.iloc[-1].exit_pre_close) <= .901
    terminal_turnover = int(w and not final_locked)
    returns = np.array([r[3] for r in records])
    returns[-1] -= terminal_turnover * one_way_bp / 1e4
    nav = np.cumprod(1 + returns)
    dd = nav / np.maximum.accumulate(np.r_[1, nav])[1:] - 1
    sd = returns.std(ddof=1)
    return {"n": len(records), "mean_daily_net_bp": float(returns.mean() * 1e4),
            "sharpe": float(returns.mean() / sd * np.sqrt(252)) if sd else None,
            "total_return": float(nav[-1] - 1), "max_drawdown": float(dd.min()),
            "exposure_fraction": float(np.mean([r[1] for r in records])),
            "one_way_trades": int(sum(r[2] for r in records) + terminal_turnover),
            "blocked_changes": int(sum(r[4] for r in records)),
            "terminal_open_position": bool(w and final_locked),
            "cost_one_way_bp": float(one_way_bp), "notional_budget_yuan": budget,
            "max_prior_adv_fraction": participation}, returns
