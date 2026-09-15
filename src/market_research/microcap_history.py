from __future__ import annotations

import pandas as pd


def build_daily_portfolio_returns(connection, *, constituent_counts=(50, 100, 200, 400, 800)) -> pd.DataFrame:
    """Build equal-weight smallest-cap returns with an explicit close-time fill lag.

    ``market_panel`` must expose date, symbol, market_cap, amount, adj_close,
    is_eligible and is_suspended. Signals use formation-date close data, orders
    execute at the next observed market close, and returns start from that
    execution close through the following market close. ``suspension_events``
    identifies confirmed suspension dates with suspend_type == 'S'.
    """
    columns = {row[0] for row in connection.execute("DESCRIBE market_panel").fetchall()}
    required = {"date", "symbol", "market_cap", "amount", "adj_close", "is_eligible", "is_suspended"}
    if not required.issubset(columns):
        raise ValueError("market_panel is missing required columns")
    if connection.execute("SELECT 1 FROM market_panel GROUP BY date, symbol HAVING count(*) > 1 LIMIT 1").fetchone():
        raise ValueError("market_panel must have unique symbol/date keys")
    counts = ",".join(str(int(value)) for value in sorted(set(constituent_counts)))
    return connection.execute(f"""
        WITH dates AS (
            SELECT date,
                   lead(date, 1) OVER (ORDER BY date) AS entry_date,
                   lead(date, 2) OVER (ORDER BY date) AS return_date
            FROM (SELECT DISTINCT date FROM market_panel)
        ), ranked AS (
            SELECT p.date AS formation_date, d.entry_date, d.return_date, p.symbol,
                   p.market_cap, p.amount, row_number() OVER (PARTITION BY p.date ORDER BY p.market_cap, p.symbol) AS size_rank
            FROM market_panel p JOIN dates d ON p.date=d.date
            WHERE p.is_eligible AND NOT p.is_suspended AND p.market_cap>0 AND p.amount>0 AND p.adj_close>0
              AND p.date <> DATE '2014-12-31'
        ), sizes AS (SELECT unnest([{counts}])::INTEGER AS constituent_count), basket AS (
            SELECT r.*, s.constituent_count FROM ranked r CROSS JOIN sizes s
            WHERE r.size_rank <= s.constituent_count AND r.return_date IS NOT NULL
        ), marks AS (
            SELECT b.*, entry.adj_close AS entry_close, n.adj_close AS next_close,
                   coalesce(entry_event.has_suspension, false) AS entry_suspended,
                   coalesce(exit_event.has_suspension, false) AS exit_suspended
            FROM basket b
            LEFT JOIN market_panel entry ON entry.date=b.entry_date AND entry.symbol=b.symbol
            LEFT JOIN market_panel n ON n.date=b.return_date AND n.symbol=b.symbol
            LEFT JOIN (SELECT DISTINCT symbol, date, true AS has_suspension
                       FROM suspension_events WHERE suspend_type='S') entry_event
              ON entry_event.date=b.entry_date AND entry_event.symbol=b.symbol
            LEFT JOIN (SELECT DISTINCT symbol, date, true AS has_suspension
                       FROM suspension_events WHERE suspend_type='S') exit_event
              ON exit_event.date=b.return_date AND exit_event.symbol=b.symbol
        ), returns AS (
            SELECT *, CASE WHEN entry_close>0 AND next_close>0
                           THEN next_close/entry_close-1 ELSE 0 END AS marked_return,
                   CASE WHEN (entry_close IS NULL OR entry_close<=0) AND NOT entry_suspended
                              OR entry_close>0 AND (next_close IS NULL OR next_close<=0) AND NOT exit_suspended
                        THEN 1 ELSE 0 END AS unknown_mark,
                   CASE WHEN entry_close>0 AND (next_close IS NULL OR next_close<=0) AND exit_suspended
                        THEN 1 ELSE 0 END AS stale_mark,
                   CASE WHEN (entry_close IS NULL OR entry_close<=0) AND entry_suspended
                        THEN 1 ELSE 0 END AS unfilled_entry
            FROM marks
        )
        SELECT formation_date, entry_date, return_date, constituent_count,
               avg(marked_return) AS return_unknown_flat,
               avg(marked_return - unknown_mark) AS return_unknown_total_loss,
               sum(stale_mark)::INTEGER AS confirmed_suspension_stale_marks,
               sum(unfilled_entry)::INTEGER AS unfilled_entry_suspensions,
               sum(unknown_mark)::INTEGER AS unresolved_missing_marks,
               CASE WHEN sum(unknown_mark)>0 THEN 'unresolved_price_sensitivity'
                    WHEN sum(stale_mark)>0 THEN 'price_complete_with_suspension_mark' ELSE 'price_complete' END AS mark_status
        FROM returns GROUP BY formation_date, entry_date, return_date, constituent_count
        HAVING count(*)=constituent_count ORDER BY formation_date, constituent_count
    """).fetchdf()
