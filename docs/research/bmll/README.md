# US liquidity pilot with BMLL

[简体中文](README.zh-CN.md)

This pilot tests whether event-level data can improve small-cap execution research. It studies quote spreads and age, trade-relative prices, a fixed comparison window and hypothetical turnover costs. It does not establish a small-cap premium, a tradable strategy, or account capacity.

## Scope and interpretation

The shared data exposes reference records, consolidated NBBO and Trades Plus. A reference label of L3 does not grant access to a full depth/order-message table. NBBO quantity is top-of-book displayed size, not a fill guarantee. No queue or deep-book simulation is supported by this pilot.

The config fixes twelve candidates, including two ETF references, two March baseline dates and five April comparison dates. Candidates are carried forward from an earlier exploratory list; this is a retrospective purposive sample, not a market-cap-selected universe fixed before April. The historical feature snapshot supplies lagged market cap and ADV20 at the first baseline date, but original release-time availability is not certified. ETF references remain separate from equities. Do not use September group assignments for March observations.

Historical reference rows are joined by date and listing ID, with uniqueness checked before aggregation. SIP consolidated listings need not have `is_primary=true`. `is_alive` describes the shared historical reference snapshot; it does not resolve survivorship or retroactive revisions. A formal study must replace the pilot selector with independently validated historical eligibility and corporate-action mappings.

## Four investigations

| Question | Pilot evidence | Remaining requirement |
|---|---|---|
| What does crossing the spread cost? | Time-weighted NBBO and trade-time effective-spread diagnostics | Freshness, fees, actual order policy and execution validation |
| What changes in a pressure window? | Paired security comparisons of spreads, quote age and displayed bid notional | More periods, matched controls and independent event selection |
| Which small companies differ? | Lagged cap/ADV20 plus observed price and activity | Filing-date fundamentals, historical identity, dilution and delisting |
| Does lower turnover help? | Explicit annual cost scenarios across holding intervals | An out-of-sample return signal, holdings and actual turnover |

The April dates are a prespecified comparison window in this pilot, not proof of causal event attribution. Compare each security's daily averages before summarising across securities. A ratio of group medians and a median of paired ratios answer different questions and may move in different directions.

## Metrics and quality controls

Quote windows are 09:30–10:00, 11:00–11:30 and 15:30–16:00 America/New_York, left-closed/right-open. Convert UTC event times with the timezone name, retaining DST behavior. Carry the preceding quote into each window; clip durations at both boundaries. Check total coverage, valid non-crossed prices and size-field coverage separately. An age of 60 seconds is a diagnostic threshold, not an exchange expiry rule. Old quotes may remain valid; new quotes need not fill. Market-state labels alone do not certify tradability.

Trade statistics cover continuous trading from 09:30 to 16:00 on the execution date matching the publication-date partition. Their open/middle/close cells are broader than the quote windows and must not be treated as identical intervals. Late reports executed on another day are excluded and not a reconciled economic tape. Signed quantity preserves cancellations for volume diagnostics; cost statistics exclude same-day trade-ID groups with cancellations/amendments. Cross-day corrections and feed identity ambiguities remain unresolved. Trade events are not automatically independent economic executions.

The full quoted spread is `(ask-bid)/mid × 10,000`. Signed effective spread is `2 × direction × (price-mid)/mid × 10,000`; the direction is +1 for aggressor code 1 and −1 for code 2. Code 0 is unknown and excluded from signed measures, with its share reported. Absolute price distance is a separate diagnostic. Taker markout is `direction × (future_mid-price)/mid × 10,000`; positive values favor the taker. Future mids are outcome labels only. Missing horizons keep their own denominators.

The cost scenario is `full_spread_bps/10,000 × 252/holding_days × replaced_fraction`. It assumes one full spread per complete round trip. It is an arithmetic hurdle, not an estimated realised loss or a forecast. Impact, fees and return signals are absent; the quoted spread need not equal the investor's effective cost.

## Reproduce privately

Use the configured Databricks CLI identity. No token is accepted by these scripts. Install the project development environment with `uv sync --locked --extra duckdb --extra dev`.

```sh
python scripts/generate_bmll_pilot_sql.py
# Set BMLL_WAREHOUSE_ID to your existing warehouse ID and BMLL_RUN_ROOT to a new private data directory.
uv run python scripts/run_bmll_query.py --warehouse-id "$BMLL_WAREHOUSE_ID" --sql sql/bmll/reference.sql --output-dir "$BMLL_RUN_ROOT"
uv run python scripts/run_bmll_query.py --warehouse-id "$BMLL_WAREHOUSE_ID" --sql sql/bmll/trades.sql --output-dir "$BMLL_RUN_ROOT"
uv run python scripts/run_bmll_query.py --warehouse-id "$BMLL_WAREHOUSE_ID" --sql sql/bmll/quotes.sql --output-dir "$BMLL_RUN_ROOT"
# BMLL_FEATURES points to the historical feature Parquet used by the original liquidity study.
PYTHONPATH=src uv run python scripts/summarize_bmll_pilot.py --input-dir "$BMLL_RUN_ROOT" --features "$BMLL_FEATURES" --output-dir "$BMLL_RUN_ROOT/analysis"
```

Each query is read-only, bounded by symbols and dates, and retains its SQL, statement ID and result. Check reference uniqueness before interpreting the joined queries. The decoder rejects partial/truncated results; increasing sample size may require explicit chunk retrieval. The runner does not provision compute or change permissions. Query execution can start the selected existing warehouse and incur compute usage.

Keep all provider-derived per-security observations and reports outside Git. Do not publish them under an assumed blanket redistribution permission. The public small-cap site can link to reviewed methodological conclusions; new numerical publication requires a separate rights and aggregation review.

Source definitions: [BMLL Trades Plus specification](https://www.bmlltech.com/files/documents/BMLL-Trades-Plus.pdf), [BMLL coverage](https://www.bmlltech.com/market-data-coverage). The local shared schema, rather than the latest PDF alone, determines which columns the queries can use.

[Follow-up experiments](followup.md)

[Historical identity reconciliation](identity.md)
