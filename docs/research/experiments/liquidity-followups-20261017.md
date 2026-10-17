# Cross-market liquidity follow-up audit (2026-10-17)

## Current findings

The four-market turnover distribution now includes P10, P25, the median, P75, P90, and the count and share of included security-days with zero ADV20. The zero share uses only security-days already present in the research feature set; it is not a denominator for the full listed universe. Empty relative-size buckets retain a zero count and a null share.

Targeted minute/daily checks show exchange concentration. In selected later-date Beijing-exchange samples, a high share of matched security-days differs by more than 1%; on 2024-11-28, 257 Beijing daily rows have no matching minute security-day and no matched suspension event. These dates were selected from earlier anomalies. They do not estimate the full history or establish an upstream cause. The data platform still needs to trace source vintages, symbol mapping and date coverage.

The targeted audit covers 31,761 daily security-day rows and records zero zero-turnover rows. A complete point-in-time history of listings, delistings and full-session suspensions was not supplied, so a true market-wide zero-trade denominator cannot be computed. Missing minute rows, missing daily rows, suspensions and unlisted securities must be resolved separately.

Cross-market comparisons remain aligned on common observation dates and disclose sample counts and observed USD cap ranges. Shared dates do not remove source differences: US turnover remains a close-times-volume proxy, Japanese shares remain exploratory, and historical universe availability is not fully established. The common-date view is conditional descriptive evidence, not a liquidity ranking.

Execution evidence still consists of selected-date static book snapshots and simulations. The study lacks sufficient real parent orders, fills, fees and synchronized book records for live calibration. Turnover budget scenarios therefore do not establish executable capacity.

## Evidence needed next

| Gap | Required evidence or action |
| --- | --- |
| Beijing minute gaps and discrepancies | Reconcile the 257 daily-only rows on 2024-11-28 or provide their reason; inspect raw minute/daily vintages and symbol mappings on high-discrepancy dates |
| Zero-trade denominator | Historical-effective listing/delisting master, full- and partial-session exchange suspensions, and the normal trading calendar |
| Live execution calibration | Privacy-reviewed parent/child orders, fills, fees, order lifecycle and synchronized order-book data |
| Cross-market definitions | Verify turnover proxies, share classes, corporate actions, historical universes and FX dates; do not extrapolate beyond common dates |

## Method limits

ADV20 uses the prior 20 contiguous market observations. Turnover distributions weight observed security-days equally. Zero ADV20 counts only existing feature rows. The minute reconciliation is a targeted sample, not an unbiased estimate. Independent review checks grouping, quantiles, counts and public aggregates on the feature files; it is not a full raw-warehouse audit and does not prove point-in-time universe eligibility.

## Reproduction

Use `scripts/audit_liquidity_followups.py` to create identifier-free aggregates for selected dates. Rebuild and independently review published statistics with `scripts/rebuild_liquidity_evidence.py`, `scripts/review_liquidity_evidence.py`, `scripts/build_liquidity_relative.py` and `scripts/review_liquidity_relative.py`. Store generated outputs under the project data root, outside the source repository.
