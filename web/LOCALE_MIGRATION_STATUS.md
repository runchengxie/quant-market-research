# Web locale audit status

The public site defaults to English and retains a persistent Chinese switch. Static verification checks visible text on the listed English routes; Playwright additionally checks text after client hydration on the report routes below.

## Hydrated browser audit

The following routes pass a visible-Han scan in the default English locale:

- `/research/factors/low-turnover/`
- `/research/factors/pb-roe/`
- `/research/microcap/`
- `/research/cashflow/` and `/research/cashflow/recovery/`
- `/research/indices/`
- `/research/liquidity/`
- `/research/microcap/cross-market-liquidity/`
- `/research/`
- `/data-sources/`
- `/search/`

## Remaining known leakage

`/research/style-factors-18y/` still exposes Chinese factor labels and factor definitions after the React workbench hydrates. A local Playwright audit counted 1,299 Han characters in visible page text. The names, historical definitions, current implementation descriptions, and related diagnostics need English presentation strings before this route can join the hydrated browser gate.

This inventory is intentionally incomplete until each public English route is checked after client hydration. Passing static HTML checks alone does not establish that an interactive route is fully localized.
