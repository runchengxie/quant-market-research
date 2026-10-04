# Market Research Plain Language Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Explain every reader-facing specialist term, formula, and source field on the Market Research site without reducing its evidence or methods record.

**Architecture:** Treat `publicPages` and `publicDocs` as the complete route inventory, then follow each rendered value to its Astro/React copy source, public dictionary, or reviewed snapshot. Add local explanations beside terms and fields using the site's bilingual content pattern; keep the original identifier and source record intact.

**Tech Stack:** Astro, React, TypeScript, Markdown, public aggregate JSON/CSV, bilingual `data-en` / `data-zh` strings.

**Spec:** `quant-factor-observatory/docs/superpowers/specs/2026-10-04-plain-language-evidence-audit-design.md` (Factor Observatory branch commit `a4fedd3`)

## Global Constraints

- Review all routes in `web/src/content/public-registry.ts` and all registered documents in English and Simplified Chinese.
- Preserve formulas, identifiers, values, units, dates, sample scope, sources, uncertainty, evidence status, and limitations.
- Do not change research calculations, source mappings, raw values, machine schemas, or publication boundaries.
- Do not infer an undocumented field definition; state the uncertainty and source boundary.
- Do not add or run tests for this editorial task; use `git diff --check`, source comparison, and required PR CI.

## Review Focus

- Barra factor names may have different historical and current calculations; preserve both versions and their verification status.
- Similar return and risk labels can use different intervals, denominators, fees, and investment bases; state those beside each displayed value.
- Trade value, turnover, capacity, and executable return are distinct; never describe a proxy as actual execution.
- Historical audit fields may be unavailable or unresolved; preserve nulls and uncertainty rather than imply zero or a verified definition.
- English and Chinese notes must preserve the same limits, dates, samples, and source status while reading naturally.

---

### Task 1: Inventory the public routes, documents, and rendered fields

**Files:**
- Create: `docs/superpowers/reviews/2026-10-04-public-term-inventory.md`
- Inspect: `web/src/content/public-registry.ts`, `web/src/pages/**`, `web/src/components/**`, `web/src/content/factors.ts`, `web/src/content/locale-copy.ts`, `web/src/conclusion-copy.ts`, `web/src/lib/factor-implementations.ts`, registered Markdown documents, and public snapshots rendered by those pages

**Interfaces:**
- Produces one row per route/locale and each interpretation-critical term, formula, chart metric, and displayed source-field identifier.
- Each row records its rendered label, verified source/definition, proposed plain-language explanation, and unresolved limits.

- [ ] Extract the exact page IDs/routes from `publicPages` and document paths from `publicDocs`.
- [ ] Follow rendered components to their exact strings and displayed snapshot fields; exclude machine-only values not shown to a reader.
- [ ] Verify meanings from source notes and public dictionaries, keeping historical/current versions separate.
- [ ] Check that overview, each research route, data/source pages, all public documents, chart legends, table columns, and controls are represented in both locales.

**Check:** Reconcile inventory route IDs against `publicPages` and document source paths against `publicDocs`; no registered page or document is omitted.

### Task 2: Explain overview, research, and market data displays

**Files:**
- Modify as needed: `web/src/pages/index.astro`, `web/src/pages/research/index.astro`, `web/src/pages/data-sources/index.astro`, `web/src/components/ResearchOverview.tsx`, `web/src/components/ResearchPage.astro`, `web/src/components/ResearchContext.astro`, route-specific page files in `web/src/pages/research/**`, and bilingual labels in `web/src/content/locale-copy.ts` / `web/src/conclusion-copy.ts`
- Update: the inventory from Task 1

**Interfaces:**
- Produces direct explanations for the overview metrics, coverage windows, benchmark and proxy terms, evidence stages, and table fields displayed across topic pages.

- [ ] Explain each chart/table's measure, unit, sample, period, and reference group at the point of use.
- [ ] Distinguish data coverage from market coverage, a proxy series from an investable portfolio, traded value from depth/capacity, and generated time from observation period.
- [ ] Preserve separate index, ETF, market, and return bases and all missing-data labels.
- [ ] Keep conclusion, evidence stage, and open question intact while defining specialist terms.

**Check:** For each changed display, match the explanation to the corresponding source contract and inventory row; no sample or metric boundary is broadened.

### Task 3: Explain factor workbenches and calculations

**Files:**
- Modify as needed: `web/src/pages/research/style-factors-18y/index.astro`, factor workbench UI in `web/src/components/react/style-page.tsx`, `web/src/components/research/BarraFactorDictionary.astro`, `web/src/components/research/BarraNarrative.astro`, `web/src/components/react/cashflow-page.tsx`, `web/src/components/react/liquidity-page.tsx`, `web/src/components/react/microcap-page.tsx`, `web/src/lib/factor-implementations.ts`, and registered Barra/turnover/low-turnover/PB-ROE documents
- Update: the inventory from Task 1

**Interfaces:**
- Produces field-by-field explanations of the exact calculations and historical definitions used by each visible workbench and factor dictionary.

- [ ] Explain descriptor, factor, factor family, cross-sectional standardization, portfolio grouping, formation date, rebalance, and point-in-time availability where shown.
- [ ] Keep formula text and code-form identifiers such as `turnover_rate` and `daily_basic.total_mv`; explain the input, operation, output unit, and direction in nearby prose.
- [ ] Keep the historical 19-factor series distinct from current reviewed definitions, including unverified sources and missing historical implementation details.
- [ ] Explain the exact components of compound factors without implying an unverified historical weight or composition.
- [ ] Preserve all dictionary columns, source records, factor caveats, and provenance.

**Check:** Compare each factor definition to `factorDefinitions`, the public dictionary, and source inventory. Confirm that historical and current calculations are not conflated.

### Task 4: Explain returns, execution, and recovery methods

**Files:**
- Modify as needed: `web/src/components/LowTurnoverExecutionEvidence.tsx`, `web/src/components/RecoverySection.tsx`, `web/src/components/ReplicationSection.tsx`, `web/src/components/MicrocapCharts.tsx`, `web/src/components/ResearchCharts.tsx`, `web/src/components/react/research-shared.tsx`, and registered documents under `docs/research/experiments/` and `docs/research/factors/`
- Inspect displayed source values in `web/public/data/**` without changing them
- Update: the inventory from Task 1

**Interfaces:**
- Produces precise plain-language explanations for performance, drawdown, turnover, fills, cash, right-censoring, missing settlement prices, replication gaps, and sample-selection fields.

- [ ] Define each return and risk value with its exact period, fee basis, compounding basis, and reference portfolio where available.
- [ ] Explain right-censoring as an observation that had not ended by the cutoff date, and distinguish it from a known recovery time.
- [ ] Explain null, missing price, zero fill, and cash weight distinctly; preserve the ledger and any unreconciled amount.
- [ ] Preserve unresolved source events, execution assumptions, selection rules, and all known limitations.

**Check:** Trace every definition to its research note or source file. Confirm unknown settlement and execution outcomes remain unknown.

### Task 5: Complete the inventory and submit the PR

**Files:**
- Review: all changed pages, components, and registered documents from Tasks 1–4
- Update: existing `web/src/*.test.mjs` or `web/src/**/*.test.mjs` string expectations only if directly invalidated by approved user-facing wording; do not add or run tests

- [ ] Mark the final rendered location for every inventory row; document unresolved definitions with the preserved identifier and source boundary.
- [ ] Compare pre-change and final pages for all numbers, formulas, units, dates, source IDs, samples, caveats, and conclusion states.
- [ ] Inspect responsive page order and native disclosure semantics when any long copy is moved into a disclosure.
- [ ] Run `git diff --check`; do not run a local test suite.
- [ ] Commit and push the market-research task branch, open a PR to `main`, and merge only after required CI passes.

**Expected result:** `git diff --check` exits successfully; every registered route, document, and interpretation-critical rendered field is accounted for in both locales; CI passes before merge.
