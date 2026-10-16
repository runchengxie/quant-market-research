# Reading empty buckets and market-relative size groups

[中文](liquidity-size-groups-20261016.zh-CN.md)

The explorer now defaults to USD 100m–1bn, where every published view has A-share observations. Empty absolute buckets state that the selected group has no eligible observations and show the market's full sample size. A missing market remains a separate period-coverage condition.

The A-share `< $10m` bucket has zero eligible observations in all five views; this does not mean that A-share source data is absent. The reviewed eligible A-share panel spans 2019-11-29–2026-10-15. Earlier screening also found 151 below-USD10m candidate security-days excluded for missing contiguous market sessions. The absence statement applies to the current eligible universe, not to every A-share security ever traded.

## Optional relative comparison

The new **Within-market size quintiles** mode uses the same eligible features, market dates, intersections, rolling statistics and FX as the [reviewed absolute release](liquidity-rebuild-20261016.md). It changes only size membership:

- At each observation date, rank eligible stocks separately within each source market by prior-session USD total market cap, ascending.
- Split using `NTILE(5)`. Equal caps use stable symbol order. Integer group sizes may differ by one; small toy populations may leave groups empty.
- Historical views pool daily memberships, equally weighting security-days. Unique stocks can cross groups and are not additive. Reported market-cap ranges span all selected security-days, not fixed daily cutoffs.

On 2025-09-30 the smallest fifth contains 884 US, 486 HK, 1,044 A-share and 731 JP stocks. Their upper market-cap bounds are approximately USD101.15m / 17.74m / 482.68m / 38.48m. This demonstrates why equal within-market rank is **not equal dollar size**. Displayed ranges retain source valuations, including extreme positive values; historical share counts and security classes have not been independently certified. Relative grouping does not repair source-universe or valuation differences.

The original absolute JSON and independent-review checksum are unchanged. The separate [relative summary](../../../web/public/data/liquidity/relative-summary.json) binds to that exact base checksum. A separate pandas/NumPy path checked daily quintile assignment and **950 aggregate cells**, including both rolling measures, sample counts and actual market-cap bounds. It also rechecks 760 original absolute cells and actual input feature hashes to reject a different feature version. Its 19,275,158 security-day entries span overlapping publication views and are not unique raw rows independently audited. See the [relative receipt](../../../web/public/data/liquidity/relative-review.json).

## Reproduction

With `PYTHONPATH=src`, the private `FEATURE_DIR` points to the earlier reviewed feature files. Keep all output/intermediates outside Git:

```sh
python scripts/build_liquidity_relative.py --features "$FEATURE_DIR" --base web/public/data/liquidity/summary.json --output "$RUN_DIR"
python scripts/review_liquidity_relative.py --base web/public/data/liquidity/summary.json --features "$FEATURE_DIR" --proposal "$RUN_DIR/relative.proposed.json" --output "$RUN_DIR/independent-review.json"
python scripts/publish_liquidity_relative.py --proposal "$RUN_DIR/relative.proposed.json" --review "$RUN_DIR/independent-review.json" --base web/public/data/liquidity/summary.json --output web/public/data/liquidity/relative-summary.json
```

The publication gate checks exact review/base checksums, aggregate field boundaries, unchanged market/date/universe metadata and count conservation. No security identifiers, raw rows or private paths enter the published artifact. Relative-file loading failure stays local and can be retried while absolute comparisons remain available.
