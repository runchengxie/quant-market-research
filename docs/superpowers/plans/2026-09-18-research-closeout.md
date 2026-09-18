# Quant Research Closeout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 收口公开研究的状态、数据新鲜度、网页展示和发布验证，不把缺少外部原始数据的研究误报为已完成。

**Architecture:** 公开快照新增统一 provenance/freshness contract，网页通过共享 TypeScript 组件读取并展示；研究算法相关工作补充 Python 回归契约和可复现入口，外部数据不可用时保持 pending。发布流程先构建 Astro、再构建 MkDocs、创建 `.nojekyll`，最后执行静态验证。

**Tech Stack:** Python/pandas/pytest/ruff，Astro/React/TypeScript/Node test，MkDocs，GitHub Pages。

**Spec:** `docs/superpowers/specs/2026-09-18-research-closeout-design.md`

## Global Constraints

- 原始行情、凭证、完整股票级运行结果继续留在仓库外。
- 不在缺少外部输入时生成或发布新的收益数字。
- `generated_at` 与数据 `as_of` 必须分开表达。
- `verified`、`derived`、`incomplete`、`exploration`、`pending` 状态不得互相替代。
- 算法行为变化必须先写失败测试，再实现最小修改。

---

### Task 1: 建立公开快照 freshness contract

**Files:**
- Create: `web/src/lib/freshness.ts`
- Test: `web/src/freshness.test.mjs`
- Modify: `web/public/data/manifest.json`
- Modify: `web/src/lib/public-data.ts`

**Interfaces:**
- `type FreshnessStatus = "verified" | "derived" | "incomplete" | "exploration" | "pending"`
- `formatFreshness(meta): string`
- `snapshotFreshness(manifest, key): SnapshotFreshness | null`

- [ ] Write tests for separating generated time from coverage end, rendering missing dates as `日期待补`, and preserving per-market dates.
- [ ] Run `cd web && npm test` and verify the new tests fail because the helpers are absent.
- [ ] Implement pure freshness parsing/formatting and extend the manifest with reviewed snapshot entries for overview, microcap, turnover, liquidity, Barra, cashflow, and indices.
- [ ] Run focused freshness tests, then all web tests.
- [ ] Commit `feat: add public snapshot freshness contract`.

### Task 2: 在共享网页壳层展示 freshness

**Files:**
- Modify: `web/src/components/ResearchPage.astro`
- Modify: `web/src/components/ResearchOverview.tsx`
- Modify: `web/src/components/react/research-shared.tsx`
- Modify: `web/src/components/react/style-page.tsx`
- Modify: `web/src/components/react/liquidity-page.tsx`
- Modify: `web/src/components/react/cashflow-page.tsx`
- Modify: `web/src/components/react/microcap-page.tsx`
- Modify: `web/src/components/react/ResearchRoutes.tsx`
- Modify: `web/src/styles.css`
- Test: `web/src/freshness-ui.test.mjs`

**Interfaces:**
- `FreshnessPanel` renders generated time, as-of/coverage, source and quality state.
- `ThemeHeading` accepts optional freshness metadata without changing existing callers.

- [ ] Write source-level tests requiring the shared panel on overview and research pages, an explicit date on the indices page, and per-market dates on liquidity.
- [ ] Run the focused UI tests and verify failure.
- [ ] Implement the shared panel and wire each page to the manifest or its source snapshot; keep existing caveats visible.
- [ ] Add CSS for compact responsive freshness badges and accessible contrast.
- [ ] Run all web tests and inspect built HTML for freshness text.
- [ ] Commit `feat: show research snapshot freshness in web pages`.

### Task 3: 修复快照构建和发布校验闭环

**Files:**
- Modify: `web/scripts/build-public-snapshot.mjs`
- Modify: `web/scripts/verify-static-site.mjs`
- Modify: `.github/workflows/pages.yml`
- Modify: `web/package.json`
- Test: `web/src/static-site-verifier.test.mjs`

**Interfaces:**
- Snapshot generation writes deterministic `generated_at` and preserves source `as_of` fields.
- Static verification accepts only a site containing Astro pages, MkDocs docs, `.nojekyll`, and no private paths.

- [ ] Add tests for missing docs output, missing `.nojekyll`, and freshness metadata failures.
- [ ] Run the focused verifier tests and verify failure against the current incomplete fixture.
- [ ] Implement deterministic validation messages and a single documented build command that builds both site layers before verification.
- [ ] Add a `build:pages` script and use it in CI/local documentation.
- [ ] Run web tests, Astro build, MkDocs strict build, touch `.nojekyll`, and static verification.
- [ ] Commit `fix: close public pages build validation`.

### Task 4: 算法研究状态与回归契约收尾

**Files:**
- Modify: `docs/research-roadmap.md`
- Modify: `docs/research/factors/microcap.md`
- Modify: `docs/research/factors/low-turnover.md`
- Modify: `docs/research/factors/barra-factor-dictionary.md`
- Modify: `docs/research/experiments/turnover-microcap-followup-20260915.md`
- Modify: `scripts/analyze_microcap_history.py`
- Test: `tests/test_microcap_history_analysis.py`

**Interfaces:**
- No new headline performance result is published without external input manifest and hash.
- Research docs expose exact next command, input gate, quality status, and expected output boundary.

- [ ] Add regression tests for fail-closed input manifest checks and explicit incomplete status when point-in-time eligibility or price vintage data is absent.
- [ ] Run focused tests and verify failure.
- [ ] Implement only the validation/status layer; keep calculations unchanged unless a test proves an existing contract violation.
- [ ] Update research documents to distinguish completed audits, pending external-data reruns, and exploratory evidence.
- [ ] Run focused Python tests, full Python tests, Ruff, and `git diff --check`.
- [ ] Commit `docs: close research algorithm status gaps`.

### Task 5: 计划文档和包体积收尾

**Files:**
- Modify: `docs/superpowers/plans/2026-09-16-astro-research-site.md`
- Modify: `docs/superpowers/plans/2026-09-15-turnover-microcap-followup.md`
- Modify: `docs/superpowers/plans/2026-09-08-*.md` where implementation evidence exists
- Modify: `docs/web-bundle-baseline.md`
- Modify: `web/scripts/report-bundle-size.mjs`

- [ ] Mark only evidence-backed completed steps as complete; retain explicit unchecked external-data gates.
- [ ] Add a current bundle measurement and document the ECharts chunk warning and acceptable follow-up.
- [ ] Run docs build, web build, bundle report, and link checks.
- [ ] Commit `docs: reconcile research plans and web baseline`.

### Task 6: 全量验证与交付

- [ ] Run Python tests, Ruff, web tests, Astro build, MkDocs strict build, static verification, and E2E if Chromium is available.
- [ ] Inspect `git diff --check`, public output for local paths/secrets, and `git status`.
- [ ] Summarize remaining external-data gates and exact freshness dates.
- [ ] Commit any test-only corrections and prepare the branch for review.
