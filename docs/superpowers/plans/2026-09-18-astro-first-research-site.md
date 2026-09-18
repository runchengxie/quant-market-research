# Astro-first 页面架构迁移 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将研究站整理为 Astro-first 页面架构，让 Astro 输出研究正文，让 React 只承担局部交互。

**Architecture:** 保留现有 Astro 路由、SiteLayout、公开 JSON 快照和 React 图表实现。先删除 React 二次路由，再把研究页面的静态内容移到 Astro，最后把剩余交互拆成可见时加载的 Islands。MkDocs 文档站保持独立。

**Tech Stack:** Astro、React、TypeScript、ECharts、Node test、CSS design tokens、GitHub Pages。

**Spec:** `docs/superpowers/specs/2026-09-18-astro-first-research-site-design.md`

## Global Constraints

- 不改变公开研究 URL、公开数据 JSON schema、Python 研究计算和 MkDocs `/docs/` 路径。
- 保留 React 只用于图表、筛选、搜索、排序和主题切换。
- 静态研究文字、标题、结论、方法、限制和可预先生成的表格由 Astro 输出。
- 每个阶段完成后运行构建或相关测试，失败时先修复再进入下一阶段。
- 保留当前中文编辑风格、数据新鲜度标注和深色模式。

---

### Task 1: 移除 React 二次路由

**Files:**
- Modify: `web/src/components/ResearchPage.astro`
- Modify: `web/src/pages/research/cashflow/index.astro`
- Modify: `web/src/pages/research/indices/index.astro`
- Modify: `web/src/pages/research/liquidity/index.astro`
- Modify: `web/src/pages/research/microcap/index.astro`
- Modify: `web/src/pages/research/style-factors-18y/index.astro`
- Modify: `web/src/components/react/cashflow-page.tsx`
- Modify: `web/src/components/react/liquidity-page.tsx`
- Modify: `web/src/components/react/microcap-page.tsx`
- Modify: `web/src/components/react/style-page.tsx`
- Delete: `web/src/components/react/ResearchRoutes.tsx`
- Test: `web/src/routes.test.mjs`, `web/src/static-site-verifier.test.mjs`

**Interfaces:**
- Astro pages import the matching named React component directly.
- `ResearchPage.astro` keeps shared metadata and freshness rendering, but no longer accepts or dispatches a route key.
- Existing React page components keep their current public exports and props.

- [ ] Step 1: Add direct imports in each Astro route page and mount the matching component with the existing hydration strategy.
- [ ] Step 2: Replace `ResearchPage.astro` route dispatch with shared shell-only markup and an optional slot for the page body.
- [ ] Step 3: Remove `ResearchRoutes.tsx` and its lazy imports after all references are gone.
- [ ] Step 4: Run `rg -n "ResearchRoute|ResearchRoutes" web/src` and verify there are no references.
- [ ] Step 5: Run `npm --prefix web run build` and `node --test web/src/routes.test.mjs web/src/static-site-verifier.test.mjs`.
- [ ] Step 6: Commit `refactor: remove react research router`.

### Task 2: 将静态研究正文移出 React

**Files:**
- Create: `web/src/components/research/ResearchContext.astro`
- Create: `web/src/components/research/ResearchSection.astro`
- Create: `web/src/components/research/MetricGrid.astro`
- Modify: `web/src/pages/research/style-factors-18y/index.astro`
- Modify: `web/src/pages/research/microcap/index.astro`
- Modify: `web/src/pages/research/cashflow/index.astro`
- Modify: `web/src/pages/research/liquidity/index.astro`
- Modify: corresponding `web/src/components/react/*-page.tsx` files
- Test: `web/src/data.test.mjs`, `web/src/recovery.test.mjs`

**Interfaces:**
- `ResearchContext.astro` accepts `question`, `evidence`, and `nextStep` strings and renders semantic summary markup.
- `ResearchSection.astro` accepts `kicker`, `title`, and a slot for static prose.
- `MetricGrid.astro` accepts a list of label, value, and note records.
- React page components return only dynamic sections and receive existing JSON/CSV data as before.

- [ ] Step 1: Extract shared context markup from `ResearchPage.astro` into `ResearchContext.astro`.
- [ ] Step 2: Move the static introduction, methods, conclusions, and limitations from the style factor page into its Astro page.
- [ ] Step 3: Move the corresponding static blocks from the microcap and cashflow pages into Astro while leaving charts and dynamic tables mounted as islands.
- [ ] Step 4: Move liquidity page static explanation into Astro and keep its interactive comparison as a React island.
- [ ] Step 5: Remove duplicated headings and static paragraphs from the React components.
- [ ] Step 6: Run `npm --prefix web run build` and `node --test web/src/data.test.mjs web/src/recovery.test.mjs`.
- [ ] Step 7: Commit `refactor: render research prose with astro`.

### Task 3: 拆分交互 Islands 和 hydration 策略

**Files:**
- Create or move: `web/src/components/islands/*.tsx`
- Modify: `web/src/components/react/research-shared.tsx`
- Modify: `web/src/components/ResearchCharts.tsx`
- Modify: `web/src/components/RecoverySection.tsx`
- Modify: `web/src/components/ReplicationSection.tsx`
- Modify: relevant Astro route files
- Test: `web/src/build-pages.test.mjs`, `web/src/static-site-verifier.test.mjs`

**Interfaces:**
- Chart components accept already validated rows or snapshot data and do not render page-level headings.
- Interactive tables accept rows and column definitions and do not own surrounding research prose.
- Critical theme controls use `client:load`. Below-the-fold charts use `client:visible`. Non-critical explorers use `client:idle`.

- [ ] Step 1: Move shared chart and table primitives into the islands boundary without changing their props.
- [ ] Step 2: Replace page-level `client:load` mounts with `client:visible` for below-the-fold charts and retain `client:load` only for ThemeToggle and immediately interactive controls.
- [ ] Step 3: Verify generated HTML contains page titles, research context, and static limitations before JavaScript runs.
- [ ] Step 4: Run `npm --prefix web run build` and `node --test web/src/build-pages.test.mjs web/src/static-site-verifier.test.mjs`.
- [ ] Step 5: Commit `refactor: isolate research interactions`.

### Task 4: 整理样式和数据边界

**Files:**
- Create: `web/src/styles/site.css`
- Create: `web/src/styles/research.css`
- Create: `web/src/styles/charts.css`
- Modify: `web/src/styles.css`
- Modify: `web/src/layouts/SiteLayout.astro`
- Modify: `web/src/components/FreshnessStrip.astro`
- Test: `web/src/design-tokens.test.mjs`

**Interfaces:**
- Existing token names remain unchanged.
- `SiteLayout.astro` imports the style entrypoints in stable order: tokens, reset/site, research, charts.
- `FreshnessStrip.astro` remains the single source for snapshot date and quality status presentation.

- [ ] Step 1: Move site-wide header, footer, navigation and base rules into `site.css`.
- [ ] Step 2: Move research report, panel, evidence card and table rules into `research.css`.
- [ ] Step 3: Move chart tooltip and chart container rules into `charts.css`.
- [ ] Step 4: Keep `styles.css` as a small compatibility entrypoint or remove it only after all imports and tests are updated.
- [ ] Step 5: Run `node --test web/src/design-tokens.test.mjs` and `npm --prefix web run build`.
- [ ] Step 6: Commit `refactor: split web styles by responsibility`.

### Task 5: 全量验证和发布分支收口

**Files:**
- Modify: only files required by failing tests or generated route assertions.
- Test: all `web/src/*.test.mjs` and `npm --prefix web run build`.

**Interfaces:**
- Static output keeps `index.html`, all existing research route pages, `docs/index.html`, `data/manifest.json`, and `.nojekyll`.

- [ ] Step 1: Run `node --test web/src/*.test.mjs`.
- [ ] Step 2: Run `npm --prefix web run build` and record Astro diagnostics and route count.
- [ ] Step 3: Run `git diff --check` and inspect `git status --short`.
- [ ] Step 4: Confirm `rg -n "ResearchRoute|ResearchRoutes" web/src` returns no matches.
- [ ] Step 5: Commit any test-only fixes with an explicit message.
- [ ] Step 6: Merge the verified branch into `main`, delete the remote/local branch and remove the worktree.

