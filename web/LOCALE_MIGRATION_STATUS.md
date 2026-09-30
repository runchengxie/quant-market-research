# Web locale audit status

The public site defaults to English and retains a persistent Chinese switch. Static verification scans the visible text in every generated English HTML route, excluding locale-suffixed `.zh-CN` companion routes. Playwright separately checks client-hydrated text on the listed routes and preserves selected-factor state and metrics when switching locale.

## Hydrated browser audit

The following route groups pass a visible-Han scan in the default English locale:

- Landing and utility pages: `/`, `/404.html`, `/research/`, `/data-sources/`, `/search/`, and the legacy `/research/recovery.html` redirect.
- Public reports: `/research/factors/low-turnover/`, `/research/factors/pb-roe/`, `/research/style-factors-18y/`, `/research/microcap/`, `/research/cashflow/`, `/research/cashflow/recovery/`, `/research/indices/`, `/research/liquidity/`, and `/research/microcap/cross-market-liquidity/`.
- MkDocs pages: `/docs/`, `/docs/research-closeout-status/`, `/docs/research/factors/low-turnover/`, `/docs/research/factors/pb-roe/`, `/docs/research/factors/microcap/`, `/docs/research/factors/smallcap-turnover-history/`, `/docs/research/factors/barra-factor-dictionary/`, `/docs/research/factors/barra-source-inventory/`, and `/docs/research/experiments/microcap-execution-diagnostic-20260928/`.

## Audit boundary

The style-factor workbench's React labels, factor definitions, execution descriptions, and research narrative now use locale-aware presentation strings. The browser test scans visible text after hydration and separately verifies that switching to Chinese preserves the selected factor and metric values. Recovery tables localize source names by stable security code and translate the expanded methodology without changing the underlying snapshot.

The browser suite also scans 24 report and utility routes after their initially visible client content hydrates, including the MkDocs-rendered documentation routes. It checks a documented style-factor locale switch and scans the recovery and replication sections after hydration, including their expanded methodology and source labels. Static output scanning covers all generated English HTML pages, but neither check proves every possible interactive state.

Scrolling the micro-cap report to its recovery section also hydrates earlier interactive research sections. That exposed additional Chinese-only micro-cap chart and narrative content outside the recovery and replication sections. Those sections are not yet localized; the route-level browser check does not scroll every section. Treat full English localization of the hydrated micro-cap workbench as an open item, and extend the browser scan section by section as it is translated.
