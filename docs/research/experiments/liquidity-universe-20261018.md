# SH/SZ liquidity scope, lifecycle sensitivity and turnover-budget ranges

The prior A-share daily aggregates mixed Shanghai/Shenzhen stocks with Beijing-exchange observations whose historical coverage remains unresolved. The release now uses SH/SZ only, excluding confirmed predecessor-code duplicates. Absolute size buckets, within-market quintiles and annual stability summaries all use this same daily scope. Minute and Level 2 audit samples retain their own previously disclosed universes.

## What changes the conclusion

On the unchanged 2020–2024 shared calendar, the $10m–$100m bucket falls from 34,947 security-days in the archived mixed scope to 500 SH/SZ security-days. Median ADV20 rises from about $200,575 to $1,169,811. This is a universe-composition change, not improved liquidity in the same stocks. Beijing coverage remains a known issue and exclusion does not establish that no comparable Beijing stocks existed.

We separately join eligible SH/SZ historical observations to the current TuShare security master. Listing dates must be on or before the previous market observation; delisting dates are exclusive. Missing lifecycle identities/dates are excluded. The same common calendar and prior-session cap buckets are retained in both variants.

| View | SH/SZ observations | After lifecycle cross-check |
| --- | ---: | ---: |
| Latest, 2026-10-15 | 4,988 | 4,988 |
| Shared snapshot, 2025-09-30 | 4,949 | 4,949 |
| 2020–2024, 1,065 shared dates | 4,710,463 | 4,710,463 |
| 2025, 161 shared dates through September 30 | 795,678 | 795,678 |
| 2026 YTD, 71 shared dates through April 30, US missing | 352,862 | 352,862 |

No observations are removed by this particular lifecycle screen. An independent pandas join also finds unchanged eligible counts in every individual year from 2015 through the 2026 cutoff. That is robustness to a retrospective cross-check, not proof of complete historical membership. Both branches inherit the same observed-bar selection, missing instruments and vendor revisions. Neither establishes a denominator containing every listed or suspended security. Earlier `bak_basic` omissions of now-delisted stocks remain a separate limitation.

## Existing history and temporal summaries

The local clean daily asset already spans January 2015 onward. The prior November 2019 lower bound was an intentional lookback window for 2020 comparisons, not a raw-data coverage gap. The full SH/SZ feature input has 11,468,748 security-days and 5,476 codes through 2026-10-15; 10,825,991 have usable ADV20. The first eligible date is 2015-02-02 after the required 20-session history.

The trend panel now includes SH/SZ history from 2015. It computes daily cross-sectional medians, monthly medians of those daily values and annual distributions over monthly values. Its P25–P75 band describes variation between observed months. These single-market annual summaries do not use the shared cross-market calendar and are not market rankings. Partial years/months and sparse size groups need their observed month counts alongside values.

## Scenario arithmetic and sample limits

The budget tool reports the selected turnover statistic × participation × days × holdings. A separate range substitutes the same group's P25 and P75 turnover statistics. It is a descriptive scenario range, not a confidence interval or evidence of executable portfolio capacity.

Holdings must be no larger than the smallest observed daily group on the exact selected calendar. An empty bucket-day contributes zero; a historical union count cannot justify concurrent holdings. Relative-group sizes follow NTILE(5), assigning remainder stocks to the earliest quintiles. Missing limits suppress the scenario. Inputs require 0 < participation ≤ 100%, 1–252 integer days and 1–1,000 integer holdings.

A daily count limit only checks an arithmetic sample-size condition. It does not prove that the same names, representative quantiles, stable participation, prices, available book depth or diversification can be achieved throughout execution. Costs, limits, suspensions and real parent-order calibration remain outside the calculation.

## Reproduction and validation

1. Build a feature directory outside the repository. Use the reviewed full-history SH/SZ features plus the unchanged reviewed US/HK/JP features. Do not duplicate or modify authoritative data. `rebuild_liquidity_evidence.py` now physically excludes Beijing and predecessor copies from A-share inputs and defaults their lower bound to 2015-01-05; `a_share_start` may override it explicitly.
2. Keep the mixed-scope baseline from commit `4b05ed2` (`web/public/data/liquidity/summary.json`); BASE below means that prior release, not the new publication. Run `scripts/prepare_liquidity_scope.py --base BASE --trial TRIAL --features FEATURES --master LISTED DELISTED --output RUN`. It verifies the trial feature/summary hashes and emits the absolute proposal, lifecycle sensitivity and scenario limits. Only aggregates are public.
3. Run `scripts/review_liquidity_evidence.py` and publish with `scripts/publish_liquidity_evidence.py`. The independent pandas/NumPy check reconciles 1,520 aggregate cells, exclusion conservation and strictly earlier FX.
4. Rebuild, independently review and publish relative quintiles with the existing relative scripts, binding them to the new absolute hash. Rebuild temporal summaries with `scripts/build_liquidity_stability.py` and verify with `scripts/review_liquidity_stability.py`; the independent pandas/NumPy pass reconciles 1,280 temporal cells.
5. Run `scripts/review_liquidity_scope.py --run RUN --master LISTED DELISTED --output REVIEW`. It independently checks lifecycle statistics and scenario daily limits, including empty group-days, using pandas/NumPy. The review receipt binds the sensitivity and scenario-limit asset hashes.

The public review receipts are `independent-review.json`, `relative-review.json` , `stability-review.json` and `universe-review.json`; the latter checks 390 sensitivity/scenario cells and contains annual lifecycle counts. Features, current security-master rows and machine paths remain outside Git. Historical PIT certification and actual execution calibration are explicitly false.
