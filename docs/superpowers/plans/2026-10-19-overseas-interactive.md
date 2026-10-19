# Overseas cost sensitivity implementation plan

**Goal:** Explore reviewed cost scenarios by ETF and input delay with exact values.
**Architecture:** A dedicated React island renders existing flat-bp aggregates with ECharts and an accessible table. The existing SVG remains a fallback and download.
**Tech Stack:** Astro, React, ECharts, existing reviewed JSON.
**Spec:** Authorized parent task: preserve research values, conclusions, sample differences and partial-2026 limits; English default with Chinese switch.

- [x] Add locale copy and cost-row adapter; verify filtering and missing values.
- [x] Build chart with ETF/delay controls, legend, exact hover and responsive theme support; integrate with overseas page.
- [x] Run relevant and complete web tests, build:pages, browser interaction checks on port 4488; commit and open PR without merging.

Review focus: missing values stay missing; each lag/ETF filters only real observations; legend operates without changing source data; language and theme changes redraw; no-JS readers retain SVG and numeric evidence.

Validation: 249 web tests passed; build:pages passed with zero Astro diagnostics and static verification; two Chromium tests passed on dedicated port 4488, covering real locale switching, dark mobile layout, exact reviewed tooltip/table values, ETF/delay controls and no-JavaScript fallback. Reviewed JSON and SVG are unchanged.

Follow-up review: merged current main including ST evidence PR #218. Browser coverage now clicks the actual canvas legend, verifies omitted-rule tooltip behavior, uses the real theme button with persisted dark preference, and asserts dark body RGB after mobile resize. ETF and lag selections persist across the real language navigation. Rebuilt and repeated all 249 unit tests plus both Chromium cases successfully.

Numeric-axis review: the 80 flat-bp scenarios use [cost, value] coordinates on a 0–40 bp value axis, with null outcomes retained. Browser assertions pin the proportional 10/20/40 bp positions and hover at the actual 10 bp coordinate. Dedicated light-desktop and dark-mobile chart screenshots are retained outside the repository; tooltip text contrast and numeric-grid theme colors are explicit.
