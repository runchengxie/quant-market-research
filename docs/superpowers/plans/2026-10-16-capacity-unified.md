# Unified Capacity Research Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline; the owner authorized execution of the recommended design. Steps use checkbox syntax.

**Goal:** Present liquidity, costs, and capacity coherently and repair theme and metric errors.

**Architecture:** A canonical liquidity entry composes existing execution evidence with a shared interactive liquidity explorer. Pure data checks quarantine inconsistent market snapshots without changing historical numbers.

**Tech Stack:** Astro, React, TypeScript, ECharts, Node test runner, Playwright.

**Spec:** `docs/superpowers/specs/2026-10-16-capacity-unified-design.md`

## Global Constraints

- Missing metrics remain missing; no guessed correction of historical aggregates.
- Default English with explicit Chinese selection, using locale catalogs.
- No raw vendor data or private paths enter published assets.
- Preserve existing study anchors and reviewed aggregates.

## Review Focus

- Missing P90 must not become a different metric.
- Pending period must not fall back to latest data.
- Conflicting counts must remove a market from comparisons.
- Dark-mode accented cards, badges, and period panels must remain readable.
- Older URLs, locale changes, and mobile layouts must remain usable.

### Task 1: Shared-surface themes

Files: `web/src/styles.css`, `web/tests/e2e/capacity-research.spec.ts`.

- [x] Reproduce dark-mode surface defects with computed-color assertions.
- [x] Replace affected backgrounds and borders with semantic variables, including accented statistics.
- [x] Check both themes and viewport sizes in the browser.

### Task 2: Liquidity data checks and explorer

Files: `web/src/lib/liquidity-quality.ts`, `web/src/liquidity-quality.test.mjs`, `web/src/content/liquidity-research-copy.ts`, `web/src/components/react/liquidity-page.tsx`.

Interfaces: `auditLiquidityMarket(market)` returns stable issue codes; `liquidityComparison(markets, bucket, metric)` returns rows with null for unavailable values; `mechanicalOrderBudget(turnover, participation, days)` returns the arithmetic budget.

- [x] Test missing P90, conflicting totals, pending periods, aligned bucket selections, and calculator bounds.
- [x] Implement checks and linked controls; show stock counts separately from observations.
- [x] Publish the quality matrix, exclusion reasons, dates and inherited-lineage limitations.

### Task 3: Unified reading and research notes

Files: liquidity/cross-market/execution Astro routes, `CapacityResearch.astro`, shared locale/registry entries, bilingual research audit notes.

- [x] Compose one canonical entry with existing execution evidence and topic anchors.
- [x] Keep existing routes usable and link to the unified entry.
- [x] Add evidence-stage notes and a bilingual audit record with reproducible checks and outstanding data work.
- [x] Update navigation labels without discarding detail pages.

### Task 4: Validate and deliver

- [x] Run web tests, build and static verification, focused browser coverage, and diff checks.
- [x] Inspect changes for private paths, unintended data changes, and parallel-task conflicts.
- [x] Commit, push, open PR, validate against latest main, merge and clean up only this task's worktree.

## Execution ledger

- Owner approved the audit recommendation and execution; no additional design or integration approval requested because workspace instructions authorize the PR workflow.
- Ruling: quarantine inconsistent inherited A-share values instead of choosing a conflicting total; neither source total is proven correct.
- Ruling: historical raw inputs and real-order calibration are evidence gaps, not fabricated additions. Audit scope and follow-up gates are visible in bilingual notes.
- Baseline: 38/39 Node file tests passed in sandbox; the failure was child-process EPERM. Re-running with process permission passed all actual unit tests.
- Independent review found a remaining embedded microcap liquidity view and calculator overflow; both fixed with regression coverage.
- Browser testing exposed locale loss on new links, exact control-label ambiguity and an English-loading/Chinese hydration mismatch. Links preserve explicit locale, controls have explicit accessible names, and the data-less server island now uses a localized fallback with client-only rendering.
- Updated against `origin/main` fe08e6e, preserving the separately merged microcap hub; its market link now targets the canonical entry.
- Combined-main validation exposed an obsolete source-text assertion for the renamed microcap hub. Updated that assertion to the current reader-facing label; numerical and behavioral expectations remain intact.

- Final local validation: 140 Node unit tests, 99 related browser tests, Astro build with zero diagnostics, static-site verification and diff whitespace check passed. Dark preview inspected visually. Independent review has no remaining Critical/Important findings.
- PR CI ran all 135 browser tests and found one additional old-title assertion in the direct-route smoke test (134 passed). Updated the expected unified title; rerunning the entire browser suite rather than skipping that check.
- Final full browser rerun: all 135 tests passed, including direct-route refresh with the unified title.
- Ruling: isolate workflow concurrency by PR number or branch ref. The fixed `pages` group cancelled this PR when the independent legacy-study task pushed. Same-PR obsolete runs still cancel; main push/dispatch still share one main-ref group. Permissions, required checks and deployment conditions are unchanged. This one-line CI correction is necessary to finish both authorized tasks without cancelling another task's run.
