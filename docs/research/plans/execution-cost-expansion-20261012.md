# Execution-cost expansion: implementation and analysis plan

The approved goal is to audit earlier versus recent L2, expand static costs using lagged liquidity covariates, and connect documented cost assumptions to an existing strategy. This extends the current study and public topic, rather than introducing a generic execution engine.

## Fixed research scope

- Historical standardized books: January 2021 on 04/15/29 and January 2025 on 02/15/27. Native books: 2026-04-07/16/24 and 2026-07-20. Dates are declared before reading cost distributions; sources missing or failing gates remain visible.
- Use the existing stock-like prefix and security-code modulo-37 selection. Retain earliest security-minute observations before checking book quality, and continuous-session boundaries [09:30,11:30), [13:00,14:57).
- Explicitly distinguish native HHMMSSmmm from milliseconds relative to 09:30 with lunch retained. Reuse the data-platform projection for canonical fields and existing static measurement mathematics.
- Compare 2021-01-04 and 2026-04-16 on common securities. Audit missing minute bins, one-sided/malformed books, source-key duplication, per-security timestamp regressions, order/trade references, event types and price-zero records. Preserve source order for sequence checks; association is not queue reconstruction.
- Standardized historical streams lack channel/business-sequence evidence. Native streams may contain those fields but ambiguous cancellations and special events remain separate gates. Include early preopening orders only with separately recorded overlap diagnostics.
- Lagged ADV, volatility and market cap use prior daily partitions only. ADV is 20 prior sessions of daily.amount × 1000; returns use close/pre_close; market cap is prior-day circ_mv × 10000. Missing history is retained. Reconstructed daily valuations do not prove historical publication-time availability.
- Compare conditional full-order costs with coverage, by date, lagged covariates and intraday bucket. Keep common securities and common valid security-minute pairs as distinct comparisons. Selected dates and stocks are not a representative sample or a causal-impact calibration.
- Reuse quant-platform to rerun an existing verified microcap diagnostic at CNY10m/100m/1bn under gross, assumed fees and borrowed fixed-cost scenarios; retain participation, T+1, price limits, partial fills and cash. Borrowed L2 quantiles remain sensitivity assumptions, not calibrated stock/time costs. Frozen-path accounting overlays are separately labeled and expose funding shortfalls.

## Implementation sequence

1. Add tests for clock profiles, invalid times, earliest-before-valid selection, duplicate/missing minute accounting, ambiguous order references, lagged covariates and missing groups; implement a bounded study runner.
2. Pin the private spec, source identity/hash/stat receipts and daily references under the external project data root. Run new outputs without replacing prior pilots.
3. Reconcile samples and measurements in an inspectable notebook; create cost/coverage comparisons and record exclusions and sequence gates.
4. Complete the independent strategy companion using shared simulator, with accounting and constrained-execution checks; combine reviewed aggregates through explicit export allowlists.
5. Update bilingual report, evidence stage and public topic with concise findings and source/sample limits. Keep all raw/per-security/event ledgers outside Git.
6. Run repository-required Python, Ruff, frontend, static and browser checks; obtain independent code/evidence review, then PR/check/merge/deploy using the standing authorization.

## Review focus

Clock conversion must not infer encoding from aliases. Window selection must precede book validity. Reference matching must distinguish presence, ambiguous keys and authenticated sequencing. Exclusions/missing covariates must retain denominators. Fees and midpoint costs must not be counted twice. Fixed-path and executable modeled returns must remain distinct. No private paths, security IDs or raw events may appear in public exports.
