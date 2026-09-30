# Web locale audit status

The public site defaults to English and retains a persistent Chinese switch. Static verification scans the visible text in every generated English HTML route, excluding locale-suffixed `.zh-CN` companion routes. Playwright separately checks client-hydrated text on the listed routes and preserves selected-factor state and metrics when switching locale.

## Hydrated browser audit

The following route groups pass a visible-Han scan in the default English locale:

- Landing and utility pages: `/`, `/404.html`, `/research/`, `/data-sources/`, `/search/`, and the legacy `/research/recovery.html` redirect.
- Public reports: `/research/factors/low-turnover/`, `/research/factors/pb-roe/`, `/research/style-factors-18y/`, `/research/microcap/`, `/research/cashflow/`, `/research/cashflow/recovery/`, `/research/indices/`, `/research/liquidity/`, and `/research/microcap/cross-market-liquidity/`.
- MkDocs pages: `/docs/`, `/docs/research-closeout-status/`, `/docs/research/factors/low-turnover/`, `/docs/research/factors/pb-roe/`, `/docs/research/factors/microcap/`, `/docs/research/factors/smallcap-turnover-history/`, `/docs/research/factors/barra-factor-dictionary/`, `/docs/research/factors/barra-source-inventory/`, and `/docs/research/experiments/microcap-execution-diagnostic-20260928/`.

## Audit boundary

The style-factor workbench's React labels, factor definitions, execution descriptions, and research narrative now use locale-aware presentation strings. The browser test scans visible text after hydration and separately verifies that switching to Chinese preserves the selected factor and metric values. Recovery tables localize source names by stable security code and translate the expanded methodology without changing the underlying snapshot.

The browser suite also scans 24 report and utility routes after their initially visible client content hydrates, including the MkDocs-rendered documentation routes. It checks a documented style-factor locale switch and scans the full A-share micro-cap workbench after hydration, including monthly turnover, the N=1 diagnostic, source notes, recovery and replication sections, and accessible chart descriptions. It also switches the micro-cap page to Chinese and back, confirming that recovery metrics retain the same numeric facts while their units and labels localize. The embedded cross-market liquidity view is also opened and scanned after switching back to English, including its coverage caveats and rolling-period label. Static output scanning covers all generated English HTML pages, but neither check proves every possible interactive state.

The micro-cap workbench coverage above exercises the A-share view and selected turnover controls, plus the embedded cross-market view's default state. Every period selector, market filter, metric, and chart interaction is not exhaustively scanned; extend stateful browser coverage when those controls are audited.
