# Liquidity evidence rebuilt — 2026-10-16

[中文](liquidity-rebuild-20261016.zh-CN.md)

Four markets now have a reproducible common-date snapshot for **2025-09-30**, plus actual historical security-day summaries. This replaces the inherited snapshot as the current descriptive evidence on the [unified research page](https://runchengxie.github.io/quant-market-research/research/liquidity/). It does not establish executable portfolio capacity or historical point-in-time availability.

## What changed

| Market | Latest usable date | Eligible stocks | Below USD 100m |
| --- | --- | ---: | ---: |
| US | 2025-10-03 | 4,411 | 870 |
| HK | 2026-05-26 | 2,383 | 1,259 |
| A-share | 2026-10-15 | 5,328 | 3 |
| JP | 2026-05-01 | 3,555 | 1,466 |

These source-specific dates are not a same-time ranking. On the common date, the eligible stock counts are respectively 4,417 / 2,427 / 5,220 / 3,654. In the USD 10m–100m bucket, stock counts are 645 / 1,006 / **0** / 1,490 and the group medians of prior-20-session mean daily turnover are approximately USD 163,109 / 11,418 / **no observations** / 100,851. An empty A-share bucket is not zero turnover and is not evidence that the source is missing.

| Historical view | Actual common-date range | Common dates | Included markets |
| --- | --- | ---: | --- |
| 2020–2024 | 2020-01-06–2024-12-30 | 1,065 | US, HK, A-share, JP |
| 2025 | 2025-01-06–2025-09-30 | 161 | All four; incomplete year |
| 2026 YTD | 2026-01-05–2026-04-30 | 71 | HK, A-share, JP; **US absent** |

Historical observations are equally weighted security-days on the intersection of included markets' available dates. A security may change size buckets: distinct-stock counts across buckets are not additive. Security-day counts are additive. Incomplete years remain visible; latest snapshots are never substituted. The November 2019 start supplies a warm-up for 2020.

## Calculation and source differences

1. Normalize native-currency turnover and total market value, preserving unique security/date keys. Duplicate keys fail rather than being silently deduplicated. Valuation and instrument joins must be one-to-one.
2. Infer a broad market calendar from dates with at least 100 observed securities. This is a source-based calendar, not proof of complete exchange sessions. A stock must have exactly the previous 20 consecutive market sessions with finite, nonnegative turnover. Observed zero is included; missing observations are not zero. No single-day fallback is used.
3. Keep **rolling mean (ADV20)** and **rolling median** separate. Market-cap buckets and source eligibility use the immediately prior contiguous market session. Summary mean/median/P90 then describe the distribution of the selected rolling measure.
4. Convert native values with the latest [ECB reference rate](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) dated strictly before the observation, at most seven calendar days old: USD per EUR divided by native currency per EUR. Reference FX is informational, not an execution price.

| Market | Turnover and market value | Scope and limitation |
| --- | --- | --- |
| US | Close × volume; close × shares outstanding, USD | SimFin positive-price universe including penny stocks; turnover is a closing-price proxy, not measured traded value. Share-class and historical-universe completeness remain unverified. |
| HK | Reported `total_turnover` / `hk_total_market_val`, HKD | RQData common stocks, listing/delisting intervals, including delisted stocks present in the instrument snapshot. Complete historical coverage is not proven. |
| A-share | `amount` × 1,000 CNY; `total_mv` × 10,000 CNY | TuShare clean daily stock panel, prior observed non-ST/non-suspended flags. Reconstructed status history and current vintages do not prove historical PIT. |
| JP | `Va`, JPY; unadjusted `C` × dated Yahoo shares | Dated domestic-equity [market codes](https://jpx.gitbook.io/j-quants-pro/api-reference/code-data-code_data/marketcode) 101/102/104/106/107/111/112/113, excluding Others and TOKYO PRO. Yahoo shares are exploratory; revision and share-class history remain unverified. |

JP has 5,914,434 positive finite prior valuations out of 5,987,248 prior-source-eligible rows (98.78%). This conditional denominator is not the entire Japanese market. The public exclusion ledger gives the full source-panel denominator. Across all markets, 26,281,668 normalized input rows produce 23,670,974 usable feature security-days; this full-span count differs from any one historical publication view.

### Sparse US dates and inherited conflicts

The first proposed run exposed 84 US rows on 84 sparse dates, including non-market dates. Using every recorded date as a session polluted rolling continuity and the latest snapshot. That proposal was retained privately but never published. The reviewed run excludes sparse dates **before** rolling and records them as `sparse_non_market_date`; a regression test covers this failure.

The inherited A-share totals (5,321 versus 5,461; below USD 100m 125 versus 177) and ambiguous rolling lineage remain unresolved historical evidence. The [archived snapshot](../../../web/public/data/liquidity/inherited-summary.json) is retained. The new A-share figures come from an explicit, separate reconstruction; they do not retroactively certify or repair the old numbers.

A backup labelled July 2026 was also checked: its US daily CSV is byte-identical to the extracted source used here, so the backup date does not extend US observations into 2026.

## Independent checks and publication boundary

- [Aggregate receipt](../../../web/public/data/liquidity/independent-review.json): a separate NumPy/pandas path reconciled **760 aggregate cells** and all grouped counts/quantiles over **19,275,158 security-day entries across publication views**. Views overlap; this is not a unique-raw-row audit. Source/exclusion counts conserve and eligible FX dates are strictly prior.
- [Source-window receipt](../../../web/public/data/liquidity/source-window-review.json): reread vendor inputs for **12 stocks per market**, sampled across the cap ordering on the common date. All **48 windows / 960 prior source rows / 336 numerical cells** agree for native mean, median, prior cap, FX and converted values. This is bounded sampling, not a complete warehouse audit or a check of original information vintages.
- Publication requires the exact independently reviewed proposal SHA-256, allowed aggregate fields, finite numbers and count conservation. Raw rows, security identifiers, private paths and detailed input receipts remain external. The public summary's SHA-256 is `59eb7b76315cd0dddc90d557c377a662c5bb71aa70e0e3eef1daf33d94199b91`.
- The runner/feature module were formatted after execution. Their execution hashes in the summary intentionally identify the archived execution versions. The [code-format receipt](../../../web/public/data/liquidity/code-format-review.json) maps those hashes to the repository files and verifies identical Python ASTs (excluding locations); calculation code did not change. The independent review scripts remain byte-identical to their receipts.

The [review notebook and reproduction guide](../../../studies/liquidity_rebuild/README.md) provide inspectable aggregate tables and saved-chart generation. Executed outputs and vendor intermediates remain outside Git.

## Execution-minute gap: localized, cause still open

The [saved-selection audit](../../../web/public/data/liquidity/minute-gap-audit.json) finds complete 26,070/26,070 sampled security-minutes on 2021-01-04. On 2026-04-16, 32,694/33,654 are present: all **80 sampled Shenzhen stocks** lack the same 12 minute keys, **09:32–09:36** and **09:54–10:00**, giving **80 × 12 = 960**. The 62 sampled Shanghai stocks have all 14,694 expected keys.

This localizes a venue/time concentration in saved sampled selections. It does not identify the upstream collection/conversion cause, validate vendor event semantics, audit the whole venue, or independently detect entirely absent securities. Existing static cost and replay measurements were not rewritten.

## Remaining work

Extend US/HK/JP observation coverage through an authorized upstream refresh; verify original vintages, instrument membership, historical share classes and Japanese shares independently. Investigate the raw collection/conversion stages around the Shenzhen gaps. Real parent/child orders, fills, participation, spread/impact and portfolio concentration are still required for calibrated capacity. The arithmetic calculator remains an explicit hypothetical budget.
