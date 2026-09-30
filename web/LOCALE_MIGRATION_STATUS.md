# Web locale audit status

The public site defaults to English and retains a persistent Chinese switch. Static verification checks visible text on the listed English routes; Playwright additionally checks text after client hydration on the report routes below.

## Hydrated browser audit

The following routes pass a visible-Han scan in the default English locale:

- `/research/factors/low-turnover/`
- `/research/factors/pb-roe/`
- `/research/style-factors-18y/`
- `/research/microcap/`
- `/research/cashflow/` and `/research/cashflow/recovery/`
- `/research/indices/`
- `/research/liquidity/`
- `/research/microcap/cross-market-liquidity/`
- `/research/`
- `/data-sources/`
- `/search/`

## Audit boundary

The style-factor workbench's React labels, factor definitions, execution descriptions, and research narrative now use locale-aware presentation strings. The browser test scans visible text after hydration and separately verifies that switching to Chinese preserves the selected factor and metric values. All twelve listed research and utility routes pass the hydrated English-text scan.

Other public routes, especially documentation routes rendered by MkDocs, are checked by static output validation. The runtime scan is not a proof for every generated path or every interactive state; add routes and states as they are audited.
