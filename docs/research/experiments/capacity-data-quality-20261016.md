# Liquidity and capacity: coverage and turnover reconciliation (2026-10-16)

[简体中文](capacity-data-quality-20261016.zh-CN.md)

## Finding

The earlier A-share “no observations” result came from an empty absolute market-cap bucket of USD 10m–100m. It did not mean that A-share daily data was absent. Daily inputs align across all four markets for 1,065 common sessions in 2020–2024 and 161 sessions through 2025-09-30. The 2026 year-to-date window has 71 common sessions for HK, A-share and JP, with US unavailable. The A-share daily panel used here runs from 2019-11-01 through 2026-10-15.

The platform also publishes an A-share TuShare 1-minute version covering 2022-07-15 to 2026-10-13: 1,019 date partitions, 1,304,100,646 rows and 5,411,206 security-days. This adds intraday evidence from the second half of 2022 onward and supports same-day reconciliation to daily turnover. It does not fill the 2020–mid-2022 minute history. The platform receipt still records nine exchange-calendar gaps, and a full native semantic rebaseline remains incomplete.

We aggregated all 1,019 minute partitions by security and date, then compared each sum with the matching daily `amount × 1,000` CNY. There are 5,411,206 matched security-days and 2,084 daily-only records, with no minute duplicate keys or invalid amounts. The median ratio of market-wide minute to daily turnover is 0.99974. Most security-days are close, but **1.76%** of matched days differ by more than 1%, about **0.09%** by more than 5%, and the maximum relative difference is about 71%. Close market-wide totals therefore do not establish agreement for every security-day.

## Source coverage

| Market | Daily research panel | Latest eligible date | Minute data | Level 2 evidence |
| --- | --- | --- | --- | --- |
| US | 2019-11-01–2025-10-04 source panel; sparse 2025-10-04 date excluded | 2025-10-03 | Not included in this cross-market panel | Not included in this cross-market panel |
| HK | 2019-11-01–2026-05-26 | 2026-05-26 | Not included in this cross-market panel | Not included in this cross-market panel |
| A-share | 2019-11-01–2026-10-15 | 2026-10-15 | 2022-07-15–2026-10-13; 1,019 published dates with nine calendar gaps | Static book snapshots on ten selected dates; event streams compared on two dates |
| JP | 2019-11-01–2026-05-01 | 2026-05-01 | Not included in this cross-market panel | Not included in this cross-market panel |

The daily historical comparisons use common dates, not the asynchronous latest snapshots. The 2020–2024 window covers 2020-01-06 through 2024-12-30 and includes all four markets. The 2025 window ends on 2025-09-30 and is incomplete. The 2026 year-to-date window covers 2026-01-05 through 2026-04-30 and includes only HK, A-share and JP. Daily inputs already support cross-market ADV20 comparisons for A-share; minute data is not required for that result.

The A-share Level 2 static sample contains 311,395 sampled security-minute books, of which 306,483 are valid and 4,912 one-sided books are excluded. These are ten preselected dates, not a probabilistic full-market sample. Order and trade event streams were compared on only two dates; event definitions, cancel semantics and cross-stream ordering remain unresolved. Existing spread, depth and order-size results remain conditional static descriptions. They are not full-market coverage estimates or actual execution costs. The other markets have no minute or Level 2 panels integrated into this study; that does not establish that no such data exists elsewhere in storage or the platform.

## A-share minute-to-daily check

The minute contract stores `amount` in CNY; TuShare daily `amount` is in thousands of CNY, so it is multiplied by 1,000. Comparisons use finite values where both frequency tables contain the same security-day. Records missing on one side remain unmatched and are not filled with zero. The matched denominator is 5,411,206 security-days.

| Check | Result |
| --- | ---: |
| Matched daily and minute records | 5,411,206 security-days |
| Daily rows without minute rows | 2,084 security-days |
| Minute rows without daily rows | 0 security-days |
| Duplicate security-minute keys | 0 |
| Non-finite or negative turnover | 0 rows |
| Absolute difference at most CNY 1 | 90.21% |
| Absolute difference at most CNY 100 | 97.36% |
| Relative difference at most 0.1% | 97.41% |
| Relative difference above 1% / 5% / 10% | 1.76% / 0.09% / 0.02% |
| Median daily market-total ratio (minute / daily) | 0.99974 |

Relative error can be large for small turnover amounts, so both absolute and relative differences are reported. The 99th-percentile security-day relative difference is about 1.63%; the maximum is about 70.92%. The share above 1% is 0.04% in 2022 (a partial year), 0.78% in 2023, 2.28% in 2024, 2.54% in 2025 and 2.22% in 2026. The rise becomes more visible after 2022, but the current evidence does not attribute it to a provider revision, symbol mapping or conversion stage. Check source vintages and the trading date before using affected security-days for ranks or cost estimates.

No recorded daily stock-day in the compared dates has zero turnover. This describes the observed TuShare rows only; it does not estimate zero-trading rates among suspended securities, securities absent from the endpoint or the whole market. Likewise, the 2,084 daily-only security-days should not be relabeled as zero-turnover minutes without further evidence.

## Intraday concentration and capacity scenarios

Observed A-share 1-minute turnover was summed across the market within each day, then summarized by across-day quantile. On days at P50 / P90 / P99, the largest single five-minute interval accounts for 8.94% / 10.51% / 12.69% of daily turnover. The 09:30–10:00 window accounts for 30.64% / 34.41% / 37.62%, and 14:30–15:00 for 12.40% / 14.27% / 16.42%. Turnover is concentrated more heavily near the open. Missing bars are not assumed to be zero. These shares do not measure order impact, book resilience or fill rates.

The interactive site scenario uses the selected market, date, group and turnover statistic as a per-stock daily benchmark:

`selected-group per-stock daily turnover × assumed participation × execution days × assumed holdings`

The result is a one-way notional sensitivity, not portfolio capital capacity. It assumes each holding trades at the same selected group statistic every day. It does not model actual constituents, suspensions, price limits, board lots, spreads, fees, queue position, cross-stock correlation or market impact, and it does not verify fills. The existing 18 strategy execution scenarios and ten-date static book measurements remain separate evidence.

## Interpretation and next steps

1. Review the security-day differences above 1% by year and symbol mapping against both source files and data versions, especially the higher rates after 2022. Keep the discrepancy visible until the cause is identified.
2. Route the nine calendar gaps and 2,084 daily-only security-days through the data platform’s existing repair and acceptance process. This study does not rewrite the platform asset.
3. Cross-market zero-turnover, intraday concentration, spreads and depth require minute and Level 2 panels for US, HK and JP under aligned eligibility, calendars and sampling rules, plus the A-share native semantic review.
4. Live capacity calibration still requires actual parent orders, fills, contemporaneous quotes, fees and identifiable participation rates. Current evidence supports historical description and hypothetical scenarios only.

## Reproduction

`scripts/audit_ashare_minute_daily.py` reads the current published minute and daily assets one date partition at a time and emits aggregate-only results without security identifiers. `scripts/build_capacity_quality_summary.py` combines the liquidity summary, minute audit, platform acceptance receipts and published Level 2 aggregates into the website dataset. Resolve input directories from the local `DATA_ROOT` and the platform's current asset contract, then pass them as command-line arguments. Raw files, security-level differences and run output remain outside the repository.

The public website summary is `web/public/data/liquidity/capacity-data-quality.json`.
