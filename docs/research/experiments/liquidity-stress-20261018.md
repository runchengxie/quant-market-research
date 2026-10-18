# Lower-turnover months, frozen size cohorts and recorded clock windows

SH/SZ daily evidence now measures within-year lower-turnover periods and the persistence of original month-end stock groups. A separate fifteen-date minute sample measures how observed turnover is distributed across recorded timestamp windows. These descriptive analyses do not establish complete historical PIT membership, achievable fills or portfolio capacity. BSE remains excluded.

## Findings and interpretation

For the 2025 $100m–$1bn group, January, February and May are the bottom three of twelve eligible months. The median of their monthly ADV20 baselines is $10,671,927, versus $12,993,368 in other eligible months: a retained arithmetic budget fraction of 82.13%, with all other inputs fixed. This is a within-year liquidity-regime comparison, not evidence that these dates could have been labeled in advance or that prices were falling.

Across twelve frozen month-end groups formed in 2025, 95.30% of stock–formation observations remain usable in the original size bucket on observation 20; 92.06% remain usable in that bucket on every observation. 99.18% remain usable on every observation when normal size-bucket migration is allowed. The endpoint migration, observed-but-ineligible and missing categories remain separate. The difference between endpoint and continuous retention matters: a stock can leave and later return.

For the same year/size group, only three minute dates are sampled: 2025-01-02, 2025-07-07 and 2025-12-31. Among 8,131 qualified security-days, the median share at recorded times 14:30–15:00 is 15.27% (P25 12.67%, P75 18.31%). This is not a full-year intraday estimate. Scaling a hypothetical full-day budget by these shares is arithmetic sensitivity, not an execution forecast.

## Daily source and lower-turnover months

The input is the previously reviewed full-history SH/SZ feature asset, bound to the published daily summary’s `a_sh_sz_features` checksum. ADV20 is the mean of the previous twenty contiguous source-market observations; capitalization and eligibility are lagged. Existing lifecycle, status-reconstruction, suspension and vendor-revision limitations remain.

Each active market date requires at least 100 eligible feature observations. Empty bucket-days contribute zero stocks but no fabricated turnover statistic. For each bucket, take the daily cross-sectional median of ADV20 and then a monthly median across observed active dates. A qualifying month needs at least ten active dates and coverage of at least 80% of that month’s active market dates. The last, incomplete source month is omitted.

Within each year/bucket, require at least six qualifying months. Select the lowest `ceil(20% × months)` monthly medians, breaking ties by month. Compare their median with the remaining months’ median. Sparse groups remain explicitly unavailable. The sample excludes unfinished October 2026; 2026 labels therefore describe available completed months, not a complete year.

The budget tool applies baseline × participation × execution days × assumed holdings to both phase baselines. Holdings cannot exceed the minimum daily eligible bucket count within that year, including zero-count bucket-days. This does not establish simultaneous availability of the same names; the separate frozen-cohort diagnostic addresses that limitation only descriptively.

These are rolling-ADV regimes. Rolling means smooth short shocks, and USD capitalization buckets and dollar turnover also change with FX, valuations and membership. This analysis does not directly measure flash crashes, locked limit days or single-day liquidation risk.

## Frozen original groups

At the last source observation of each completed month, freeze eligible names in each prior-cap bucket. Use a formation only if the next twenty source observation dates are available. Do not substitute newer names for missing or ineligible originals.

On the twentieth date classify every original stock as:

- usable and still in its original size group;
- usable but in a different size group;
- observed but failing the source feature filters;
- missing from the source observation.

The four endpoint states conserve the original denominator. Continuous retention requires usable original-bucket membership on all twenty dates; leaving and returning does not pass. Continuous usability instead requires usable observations on every date while allowing size-bucket migration; crossing a size threshold alone does not make a holding unusable. Annual fractions pool stock–formation observations, so larger formation groups have greater weight. Missing records are not automatically suspensions or zero turnover.

A second diagnostic compares the minimum future daily median ADV20 of observed usable original names with their formation-date median. It is reported only when at least 90% of original names remain usable on every future date. Display the number of passing formations and the lowest coverage across all formations alongside it. The remaining missing names can still bias this ratio. This is not a complete balanced-portfolio liquidation test, and its median across formation groups is not a worst-case guarantee.

## Selected minute dates and windows

From the existing 1,019-date reconciliation audit, retain dates with no duplicate minute keys and market-wide minute/daily turnover ratios in [0.995, 1.005]. For each observed year, choose the first, middle (`floor(n/2)`) and last retained date. Fifteen dates cover selected observations from July 2022 through October 2026. Selection is deterministic, not probabilistic or representative.

For each sampled date:

1. Start with eligible canonical SH/SZ feature names; exclude BSE and confirmed predecessor copies.
2. Check minute key uniqueness, finite nonnegative turnover, matching timestamp date and allowed recorded trading clocks. The daily asset must also have unique security keys.
3. Require at least 240 recorded bars, positive full-day turnover and minute totals within 1% of daily `amount × 1,000` CNY. Keep separate exclusion reasons for absent daily/minute data, nonpositive totals, short days and amount mismatches.
4. Divide observed window turnover by full observed minute turnover, including any auction bars. An entirely absent window stays missing; genuine recorded zero turnover remains zero.

Recorded-clock filters are 09:30 ≤ t < 10:00, 10:00 ≤ t ≤ 11:30, 13:00 ≤ t ≤ 15:00, 14:30 ≤ t ≤ 15:00, and the union of 10:00–11:30 with 13:00 ≤ t < 14:30. Windows overlap and cannot be added. Timestamp filtering and a 240-record threshold do not establish bar-interval semantics or complete coverage. Minute native semantic review remains incomplete.

P25/P50/P75 window shares pool qualified security-days within each sampled year/bucket. The UI scales a hypothetical full-day budget by those percentiles, independently of the daily group-budget calculator. Missing samples remain unavailable, especially before 2022. This range is neither a confidence interval nor evidence of fillability or impact.

## Reproduction and independent checks

All raw inputs and intermediate results remain outside Git. Pass explicit external paths; the builder rejects an output directory inside the repository.

```text
python scripts/build_liquidity_stress.py --features FEATURES --base ABSOLUTE_SUMMARY --minute-root MINUTE --daily-root DAILY --date-audit PRIOR_PRIVATE_AUDIT --output RUN
python scripts/review_liquidity_stress.py --features FEATURES --proposal RUN/summary.proposed.json --minute-root MINUTE --daily-root DAILY --output RUN/independent-review.json
python scripts/publish_liquidity_stress.py --proposal RUN/summary.proposed.json --review RUN/independent-review.json --base ABSOLUTE_SUMMARY --output PUBLIC_AGGREGATE
```

The independent reviewer reconstructs observation states in dense arrays, recomputes all month classifications and frozen cohorts with NumPy/pandas, and rebuilds all fifteen raw-minute date windows in SQL. It checks 8,549 cells and 439 formation groups. The publication gate binds exact reviewed bytes and the source feature hash, checks endpoint/qualification conservation, validates window quantiles and rejects local paths or security identifiers. Only `stress-persistence.json` and `stress-review.json` are published; private monthly, formation and window intermediates stay external.
