# Frozen-name dollar budgets, consecutive-month minute probe and revision gate

The reviewed SH/SZ feature scope now supports per-name dollar-budget diagnostics. Twenty-four 2024–2025 month ends yield 118,684 original stock–formation observations and 2,373,680 subsequent session paths, ending 2026-01-30. This is retrospective notional coverage, not share-accounting liquidation, a tested strategy portfolio or achievable fills. BSE remains excluded; historical PIT certification and actual execution calibration remain incomplete.

## Findings

For the 2025 $100m–$1bn group, assume $1m per original name and 3% turnover participation. There are 32,161 stock–formation observations.

| Subsequent source sessions | Raw observed-turnover coverage | Guarded coverage | Guarded insufficient budget, complete evidence |
| --- | ---: | ---: | ---: |
| 1 | 4,317 | 4,236 | 27,925 |
| 5 | 24,664 | 24,256 | 7,905 |
| 20 | 32,106 | 32,105 | 56 |

After five sessions, 24.58% remain uncovered under the guarded rule. The uncredited dollar fraction is 7.29%; the largest 10% of deficits contribute 67.31% of that fraction. After twenty sessions, 56 remain uncovered, so no all-name twenty-session completion maximum is reported. Among observations covered by twenty sessions, first credited-coverage day P50/P95 is 3/9. Those percentiles exclude uncovered names and are not whole-portfolio completion times.

Different formations are pooled rather than held simultaneously in one account. The tail concentration is across stock–formation observations, not the concentration of an actual investment account. These results motivate per-name tail controls beyond group-median arithmetic.

## Construction and scope

Freeze every eligible name in its lagged USD-cap bucket at each 2024–2025 source month end. Require twenty subsequent source sessions. Do not drop original names when future eligibility or capitalization changes. Annual results pool stock–formation observations; the same security can recur. Sparse buckets expose their denominator: the 2024 $10m–$100m group contains only fifteen observations; its 2025 counterpart is empty.

For each original name, credit subsequent `daily.amount × 1,000 × prior feature USD/CNY × participation` against a fixed USD notional. Feature FX is strictly earlier than the observation date and at most seven days old. This uses realized future amounts descriptively, not an advance-known volume forecast. The static comparison holds formation ADV20 fixed. Amounts are $100k/$1m, participation 1%/3%/5%, horizons 1/5/20 sessions.

Fixed-dollar accounting does not track formation-date shares, price-driven inventory valuation, FX-driven inventory valuation or corporate actions. This is not an executable exit-time estimate.

## Sell sensitivity and unknown evidence

[Daily documentation](https://tushare.pro/document/2?doc_id=27) defines amount in thousands CNY and says suspended periods have no daily records. A missing daily row alone therefore does not independently establish suspension. [Price-limit data](https://tushare.pro/document/2?doc_id=183) supplies daily bounds; [suspension events](https://tushare.pro/document/2?doc_id=214) distinguish event types and intraday timing.

Only `S` events with empty intraday timing establish full-day suspension here. They credit zero unless positive daily turnover contradicts the event, in which case evidence is unknown. Intraday suspension does not automatically discard the observed day's total. The guarded sell rule discards all turnover on any lower-limit-touch day, with a half-tick comparison tolerance. A low more than CNY0.011 below the lower limit is a conflict. Upper-limit touches do not block sells. Missing limits or invalid prices leave the guarded amount unknown.

Path states conserve rows: 2,351,279 credited, 19,783 lower-limit touches, 2,615 full suspensions and three missing daily records. No valid-daily/missing-limit path occurs in this particular sample; this does not establish coverage elsewhere or for BSE.

Unknown records are not imputed as zero turnover. Known credit may already cover the amount despite another missing day; otherwise distinguish insufficient budget with complete evidence from unresolved deficits. Uncredited balances measure unsupported hypothetical amounts, not observed unsold positions. Covered-only day percentiles retain that qualifier. A complete maximum is unavailable unless every original observation is covered.

Discarding a touched-limit day is a deliberately conservative sensitivity relative to the raw arithmetic. It is not a lower bound on achievable execution: touched days can contain sellable periods, while other daily amounts may contain inaccessible auction, after-hours or other trades. Queues, board lots, fees, impact, endogenous participation feedback and order fills are absent.

## Consecutive-month minute probe

All eighteen January 2025 source dates yield 89,250 qualified SH/SZ stock-days. Qualification requires at least 240 unique records, positive daily totals, and minute/daily amount agreement within 1%. Excluded candidates remain in daily ledgers. Finite nonnegative minute amounts and native dates/clocks are checked. SQL window amounts are independently regrouped with pandas at relative tolerance 1e-10 and absolute tolerance CNY0.01.

| Recorded-clock filter | Median turnover share |
| --- | ---: |
| 09:30 ≤ t < 10:00 | 28.30% |
| 09:30 < t ≤ 10:00 | 28.27% |
| 14:30 ≤ t ≤ 15:00 | 13.39% |
| 14:30 < t ≤ 15:00 | 13.11% |

The per-stock-day absolute opening-boundary difference has P95 2.46 percentage points. Differences between column medians are not medians of row differences. This fixed-month, all-qualified-name probe is independent of the frozen-cohort controls and is not representative of other periods or executable order windows.

[Stock minute documentation](https://tushare.pro/document/2?doc_id=370) defines amount in CNY and calls `trade_time` trading time, without defining interval endpoints in the reviewed page. Boundary sensitivity does not establish the correct convention. Existing conservative execution-engine timestamp assumptions remain assumptions; no engine settings changed and no supplier messages were sent.

## Exact feature revisions and publication

`audit_liquidity_revision.py` checks identical column names/types, nonnull unique keys, finite nonnull floats, and exact equality of every nonkey field. It separates changed rows, removed keys, historical-date additions and new-date additions. Historical changes return `review_required` and exit 2; new dates alone may return `append_only`.

The baseline is bound to its frozen SHA256. Replacing published SH/SZ feature bytes through `publish_liquidity_evidence.py` now requires `--revision-review`, bound to both old and candidate hashes. Missing, stale or historical-revision receipts stop before output replacement. Existing exact aggregate review remains required; an unchanged feature version retains that flow.

This run compares identical bytes only: 11,468,748 feature rows, 2015-01-05–2026-10-15. It establishes a baseline rather than proving longitudinal vendor stability. Retain the dated prior input outside Git; do not treat a mutable latest alias as an independent baseline. Raw daily/minute partition revisions need their own source receipts and recomputation. No new scheduled jobs or shared publication pointers were created.

## Reproduction

All inputs and intermediates remain external. `FEATURES` is the published SH/SZ feature file; `BASE` is the public daily summary; `DAILY` and `LIMIT` contain date-partition directories; `SUSPENSIONS` is the event file. `BASELINE_SHA` comes from the original publication's feature receipt, not the candidate file.

```text
python scripts/build_liquidity_exit.py --features FEATURES --base BASE --daily-root DAILY --limit-root LIMIT --suspensions SUSPENSIONS --output RUN
python scripts/review_liquidity_exit.py --run RUN
python scripts/probe_liquidity_minutes.py --features FEATURES --minute-root MINUTE --daily-root DAILY --output RUN/minute-probe
python scripts/audit_liquidity_revision.py --baseline FROZEN_FEATURES --expected-baseline-sha256 BASELINE_SHA --candidate CANDIDATE_FEATURES --output RUN/revision-baseline
python scripts/publish_liquidity_exit.py --run RUN --base BASE --output PUBLIC_LIQUIDITY_DIRECTORY
```

For a later daily-summary replacement, pass the matching `--revision-review RUN/revision-baseline/revision-review.json` to `publish_liquidity_evidence.py` in addition to its normal exact-byte aggregate review arguments. A detected rewrite needs investigation; the receipt is not permission to relabel it as an append.

Independent source SQL and pandas membership/session/pivot reconstruction check 2,772 aggregate cells, all 2,373,680 paths and 1,010 raw daily/limit partitions. Publication binds exact reviewed bytes and the existing feature checksum. The public assets are `exit-exploration.json`, `exit-review.json`, `minute-clock-probe.json` and `revision-baseline.json`. Original security identifiers, per-name bottleneck ranks, the companion notebook and run paths remain external.
