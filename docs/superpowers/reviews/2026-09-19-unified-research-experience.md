# Unified research experience review

Date: 2026-09-19

The current branch was checked with the five representative routes required by the plan at widths 320, 390, 768, 1280 and 1440. The browser assertions covered both the default light theme and a dark/reduced-motion storage-blocked case.

The required visual matrix was also rendered with Playwright: 5 routes × mobile (390px) / desktop (1440px) × light / dark = 20 combinations. Evidence was written to `/tmp/qmr-visual-<route>-<viewport>-<theme>.png` on the SSH host; the representative home mobile, Barra desktop, and Barra document mobile-dark images were additionally inspected with `view_image`. The initial inspection found the expected long-table/code overflow on narrow screens; CSS wrapping and bounded table layout were fixed, then the six unified-experience tests passed at 320, 390, 768, 1280 and 1440px.

| Route | 320/390 | 768 | 1280/1440 | Notes |
|---|---|---|---|---|
| `/` | checked | checked | checked | Single h1, compact shared navigation, no horizontal overflow. |
| `/research/style-factors-18y/` | checked | checked | checked | Factor controls and linked methodology remain readable. |
| `/research/factors/low-turnover/` | checked | checked | checked | Report numbers remain visible; topic navigation reaches real anchors. |
| `/research/microcap/` | checked | checked | checked | Research shell and resource content remain within viewport. |
| `/docs/research/factors/barra-factor-dictionary/` | checked | checked | checked | Article shell, legacy anchors and factor return link work. |

Additional checks: seven public documents, research/data/search directories, Barra factor recovery, search query round-trip, and public snapshot contract. No research data files under `web/public/data` were changed.

Known non-blocking item: Astro/Rolldown reports a pre-existing large-chunk warning during the static build; the build remains successful and the large research data is still lazy-loaded from public snapshots.

The Barra workbench no longer overrides the site-wide light/dark palette. It keeps its denser information layout and chart semantics, while inheriting the same paper/surface/ink/accent tokens as the home, research, and documentation pages.

Independent read-only review completed after task 9. No Critical findings. The reviewer identified two Important findings and three Minor findings; all were addressed before integration: freshness text now uses semantic dark-mode tokens, the microcap line chart now exposes a complete expandable data table, direct `npm run build` now writes `.nojekyll`, search/document links use `BASE_URL`, and the mobile navigation updates its accessible label when expanded. The follow-up targeted suites passed after these fixes.
