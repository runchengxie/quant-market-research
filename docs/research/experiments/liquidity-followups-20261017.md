# Cross-market liquidity follow-up audit (2026-10-17)

## Current findings

The four-market turnover distribution now includes P10, P25, the median, P75, P90, and the count and share of included security-days with zero ADV20. The zero share uses only security-days already present in the research feature set; it is not a denominator for the full listed universe. Empty relative-size buckets retain a zero count and a null share.

Targeted minute/daily checks show exchange concentration. In selected later-date Beijing-exchange samples, a high share of matched security-days differs by more than 1%; on 2024-11-28, 257 Beijing daily rows have no matching minute security-day and no matched suspension event. This is treated as a known TuShare coverage limitation: its Beijing Stock Exchange minute coverage is insufficient for this panel. Unmatched records remain source-coverage gaps, not evidence of zero trading.

The targeted audit covers 31,761 daily security-day rows and records zero zero-turnover rows. The recovered A-share monthly candidate archive covers 112 of 132 requested months; the other 20 months were backfilled with 51,174 traded-security rows only. Those rows omit non-trading and suspended members and are not a point-in-time market universe. A true market-wide zero-trade denominator cannot be computed. Missing minute rows, missing daily rows, suspensions and unlisted securities must be resolved separately.

Cross-market comparisons remain aligned on common observation dates and disclose sample counts and observed USD cap ranges. Shared dates do not remove source differences: US turnover remains a close-times-volume proxy, Japanese shares remain exploratory, and historical universe availability is not fully established. The common-date view is conditional descriptive evidence, not a liquidity ranking.

Execution evidence still consists of selected-date static book snapshots and simulations. The study lacks sufficient real parent orders, fills, fees and synchronized book records for live calibration. Turnover budget scenarios therefore do not establish executable capacity.

## Evidence needed next

| Gap | Required evidence or action |
| --- | --- |
| Beijing minute gaps and discrepancies | Obtain a sufficiently complete, independently checked Beijing Stock Exchange minute source if minute-level analysis is needed |
| Zero-trade denominator | Historical-effective listing/delisting master, full- and partial-session exchange suspensions, and the normal trading calendar |
| Live execution calibration | Privacy-reviewed parent/child orders, fills, fees, order lifecycle and synchronized order-book data |
| Cross-market definitions | Verify turnover proxies, share classes, corporate actions, historical universes and FX dates; do not extrapolate beyond common dates |

## Method limits

ADV20 uses the prior 20 contiguous market observations. Turnover distributions weight observed security-days equally. Zero ADV20 counts only existing feature rows. The minute reconciliation is a targeted sample, not an unbiased estimate. Independent review checks grouping, quantiles, counts and public aggregates on the feature files; it is not a full raw-warehouse audit and does not prove point-in-time universe eligibility.

## Reproduction

Use `scripts/audit_liquidity_followups.py` to create identifier-free aggregates for selected dates. Rebuild and independently review published statistics with `scripts/rebuild_liquidity_evidence.py`, `scripts/review_liquidity_evidence.py`, `scripts/build_liquidity_relative.py` and `scripts/review_liquidity_relative.py`. Store generated outputs under the project data root, outside the source repository.

## Follow-up evidence added (2026-10-17)

The public `liquidity/stability.json` summarizes 2019–2026 observations by market, year and absolute USD size bucket. It first computes daily cross-sectional medians of prior-20-session ADV and ADV divided by prior-session market capitalization, then takes a median across daily medians within each month. Annual summaries report the median and P25–P75 across observed monthly values, plus observed months and security-days. The band describes temporal spread, not a confidence interval. An interactive market/bucket selector exposes the yearly chart and table.

ADV20/market-cap adds a scale-adjusted turnover measure, but it cannot make source universes, turnover definitions, security classes or historical availability identical. Common-date results remain conditional descriptions, not a fully standardized market ranking. Actual-order calibration remains blocked on private parent-order lifecycle, fills, actual fees and synchronized quotes; simulated orders validate the workflow only. ADV-based budgets remain notional sensitivities rather than demonstrated capacity.
