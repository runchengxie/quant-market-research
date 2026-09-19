# 全站统一研究阅读体验 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有研究图表、7 份公开说明、目录与搜索整合为同一套清晰、可访问、可追溯的研究网站，保留旧链接和全部研究数值。

**Architecture:** Astro 统一生成公开页面，共用导航、视觉规则和三类阅读布局；React 仅处理需要状态的交互。明确的公开内容注册表控制 Markdown 加载、相关链接与搜索，版本化因子记录供专题和文章复用。切换文档路由时同时切换 Pages 构建，MkDocs 只生成不发布的参考预览。

**Tech Stack:** 当前锁定的 Astro 7、React 18、TypeScript、ECharts、Node 22、Playwright；Python 3.11+、uv、pytest、Ruff、MkDocs。不升级框架，不新增运行时后端。

**Spec:** `docs/superpowers/specs/2026-09-19-unified-research-experience-design.md`（用户已于 2026-09-19 批准）。

## Global Constraints

以下约束从规格原文摘录；适用于每个任务，不因任务未重复书写而失效。

- 所有现有公开研究页面、首页、404 页面，以及现有 7 份公开说明。
- 全站链接统一处理 `/quant-market-research` 前缀。
- `/data/` 继续只存放既有公开快照，不能用新的页面占用它。
- 每页仅一个正文 `h1`；品牌使用链接而非全站重复 `h1`。
- 正文默认 16px，辅助说明通常不低于 13px；主题标题约 28–40px。图表标签桌面不低于 12px，手机不靠缩小字号容纳全部信息。
- 页面最大宽度约 1240px，文章正文最大约 46rem；小屏保留 16–20px 页边距。间距使用同一套 4/8/12/16/24/32/48px 等级。
- 历史收益、Quality 快照、市值 v2 派生数据保持不变；本次不运行快照发布器或研究重算来完成视觉迁移。
- 未列入的规格、计划、运行手册、内部记录既不产出页面，也不进入搜索、站点地图或浏览器 bundle。
- 保留 PR #100 的 React Web Streams 渲染修复。
- 查询不发送到外部搜索服务，不增加分析追踪。
- 全文索引目标不超过 250 KiB 未压缩，超出需删去重复片段或按需拆分。
- 320、390、768、1280、1440px 检查页面无全局横向溢出；大表只在自身容器横向滚动。
- 浅色、深色、跟随系统下，正文对比度至少 4.5:1；大字号及关键控件至少 3:1。键盘焦点可见，菜单、目录、搜索、筛选和分页可操作。
- 独立审查、PR 必需检查和部署完成后再清理任务分支／工作树；主检出干净时仅快进同步。

## Review Focus

以下五类风险已落实为所属任务中的测试，不能仅依靠最后人工看页面。

1. 中文旧锚点、重复标题、编码后的 fragment：旧书签应定位到对应正文，不能只返回一个 HTTP 200 页面（任务 1、4）。
2. 同名 `size`／`quality` 属于不同实现：必须展示各自方向、来源与核验程度，不能用现行公式背书历史收益（任务 2、6）。
3. 必需或可选请求失败、空数组及重试：不得无限转圈、把缺失显示为零或阻断无关模块（任务 6、7、8）。
4. 新增内部 Markdown、相对路径越界及索引泄露：不在白名单中的文件不能加载、渲染或搜索到（任务 1、4、8）。
5. 禁用存储、跟随系统、手机键盘导航及减少动态效果：网站仍可读可操作，主题在同站页面间保持一致，不能出现不可退出的菜单（任务 3、9）。

---

## 执行前提、范围与检查命令

本文件是待审阅的计划，不表示产品已经实现或重新通过测试。产品基线为 `af5b8b9cf8d7075325b1a0e9617465956bded1d4`；规格提交为 `4a39c1f847f62507e62f02bc71bab5b44e293b1b`。当前规划分支为 `docs/unified-research-experience`，位于独立工作树；执行前重新检查实际 HEAD 和用户改动。若 main 已变化，先审查差异再整合，不覆盖他人工作。

这是一项统一发布链路的改造，不拆成互不相容的独立网站。内部任务可以分别提交，不能把一半文档迁移的产物提前发布。默认按任务 1–10 顺序执行；2 和 3 的初稿可以独立进行，4 必须等 1–3 的接口稳定，8 必须等公开正文结构稳定。禁止并行修改共享的 `styles.css`、注册表或发布配置。

本文命令默认在 SSH Linux 任务工作树根执行；前端命令显式使用 `cd web` 子 shell。本地 PowerShell 保持 `login:false`。本阶段不执行安装与网站构建；以下命令仅在用户批准计划和执行方式之后执行。

```bash
git status --short
git branch --show-current
git worktree list
git fetch origin
node --version
uv --version
(cd web && npm ci)
uv run --locked --extra duckdb --extra dev pytest -q
uv run --locked --extra dev ruff check src tests scripts
(cd web && npm test && npm run build:pages)
(cd web && npx playwright install chromium && npm run e2e)
git diff --check
```

原有完整测试失败时先定位并记录基线，不以删除断言、跳过检查或修改研究快照消除失败。前一轮 Python 204、前端 91、浏览器 25 只是历史记录，不作为本轮的实际结果。

## 文件边界与责任

| 文件／单元 | 责任 | 不承担的责任 |
| --- | --- | --- |
| `web/src/content/public-registry.ts` | 公开页面、方法路径、主题关系与导航元信息 | 不读取文件，不含私有目录 |
| `web/scripts/site-contract.mjs` | 捕获和比较正文锚点、公开快照摘要 | 不发布或改写数据 |
| `web/src/content/factors.ts` | 历史因子名称、方向、解释与映射 | 不重新计算收益 |
| `web/src/content/factor-records.server.ts` | 读取唯一 YAML 字典、版本化装配公开记录 | 不进入客户端依赖图 |
| `web/src/lib/factor-links.ts` | 已知因子参数与双向链接 | 不执行任意 URL 或参数 |
| `web/src/layouts/SiteLayout.astro` | 全站外壳、主题启动、跳至正文 | 不加载研究大数据 |
| `web/src/components/ResearchPage.astro`、`web/src/layouts/ArticleLayout.astro` | 专题与方法的阅读结构 | 不各设一套颜色和导航 |
| `web/src/content/public-docs-loader.ts` | 逐个白名单读取正文、展开公共片段、构建内容集合 | 不遍历整个 docs 树 |
| `web/src/content/rehype-public-docs.ts` | 正文链接、稳定章节 ID、兼容锚点 | 不用正则重写整个 Markdown 文法 |
| `web/src/components/ChartFrame.astro`、`web/src/components/react/ChartFrame.tsx` | 相同样式的 Astro／React 图表外壳 | 不为统一强制改写图形库 |
| `web/src/lib/search.ts`、`web/src/pages/search-index.json.ts` | 公开索引、确定性的中文／英文检索 | 不联网搜索、不读原始行情 |
| `web/scripts/build-pages.mjs`、`.github/workflows/pages.yml` | 同一个可复现发布入口 | 不让 MkDocs 覆盖 Astro 文档 |

维持既有 `docs/assets/theme-tokens.css` 为唯一色彩／字体 token 源，更新其内容并去掉远程字体导入；公开 Astro 与非公开 MkDocs 预览均引用它。无需为了目录美观复制第二份 token 文件。`styles.css` 只对本次涉及的共享外壳、文章、控件、图表进行有界拆分或整理，不做无关重构。

## Task 1: 固定旧站兼容合约与公开内容注册表

**Files:**

- Create: `web/src/content/public-registry.ts`
- Create: `web/scripts/site-contract.mjs`
- Create: `web/tests/fixtures/legacy-site-contract.json`
- Create: `web/tests/fixtures/public-snapshot-hashes.json`
- Create: `web/src/public-registry.test.mjs`
- Create: `web/src/site-contract.test.mjs`
- Modify: `web/src/lib/routes.ts`（保留现有导出与 hash 映射）
- Read: `mkdocs.yml`、`web/src/routes.test.mjs`、所有旧公开路由。

**Interfaces:**

```ts
export type SectionId = 'overview' | 'research' | 'docs' | 'data';
export type TopicId = 'cashflow' | 'microcap' | 'style' | 'low-turnover' | 'indices' | 'liquidity';
export type PublicPage = {
  id: string; route: string; title: string; summary: string;
  section: SectionId; topic?: TopicId; aliases: readonly string[];
  related: readonly string[]; snapshotKeys: readonly string[];
};
export type PublicDoc = PublicPage & { source: string; slug: string };
export const publicPages: readonly PublicPage[];
export const publicDocs: readonly PublicDoc[];
export function validateRegistry(pages: readonly PublicPage[], docs: readonly PublicDoc[]): void;
export function pageForRoute(route: string): PublicPage | undefined;
```

`source` 相对仓库根，例如 `docs/index.md`；`slug` 为 `/docs/` 后的路径且无首尾斜杠，首页为空字符串。`publicPages` 包含目录和方法元信息；`publicDocs` 是其中有正文源的 7 项，不额外复制一套元信息。搜索页不索引自身。ID、route、source 唯一，所有 related 必须存在，未知 snapshotKey 构建失败。

`site-contract.mjs` 导出 `collectHeadingAnchors(html: string): Promise<Array<{id: string, text: string, level: number}>>`、`hashPublicFiles(root: string): Promise<Record<string,string>>`、`captureSiteContract(dist: string): Promise<object>`。CLI 为 `capture <dist> <contract-file> <hash-file>` 与 `check <dist> <contract-file> <hash-file>`；capture 仅在旧版本构建后执行一次，文件已存在时拒绝覆盖。check 比较路由、正文锚点和所有原数据文件的 SHA-256；不把 React 自动 ID、菜单 ID 冻结为正文合约。正文选择器兼容 Astro 的 `main` 与旧 MkDocs 的 `[role="main"]`，收集 h1–h6 的现有 id 和正文内显式命名锚点。

capture 的 route 集合固定为规格的 8 个旧研究页、7 个旧方法页、首页及根 404；不得把注册表中尚未实现的新目录当作旧站必需输出，也不得跳过缺失的旧路由。check 验证兼容 alias 的真实 DOM 目标，允许标题文案改善，不强制标题字面文本不变；新目录与搜索由最终静态 verifier 和浏览器测试另外覆盖。

- [ ] **Step 1: 在旧代码上安装并运行前述基线检查。** 此时尚未修改 MkDocs、样式和页面。若依赖服务暂不可用按网络规则重试，不读取或输出 token。记录实际命令、HEAD 和结果。
- [ ] **Step 2: 增加红测试。** 在两个新 `.test.mjs` 文件中分别加入下面的断言，运行 `node --import tsx --test src/public-registry.test.mjs src/site-contract.test.mjs`（`web` 目录）。预期首次因为模块不存在而失败；实现后补齐坏输入断言，不把 import 失败当最终功能覆盖。

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { publicDocs, publicPages, validateRegistry } from './content/public-registry.ts';
test('only seven reviewed documents are admissible', () => {
  assert.equal(publicDocs.length, 7);
  assert.equal(publicDocs.filter(d => d.route === '/docs/').length, 1);
  assert.ok(publicDocs.every(d => !/superpowers|runbooks/.test(d.source)));
  assert.doesNotThrow(() => validateRegistry(publicPages, publicDocs));
  assert.throws(() => validateRegistry([...publicPages, publicPages[0]], publicDocs), /duplicate/i);
  assert.throws(() => validateRegistry(publicPages, [{...publicDocs[0], source: '../private.md'}]), /source|allowlist/i);
});
```

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { collectHeadingAnchors } from '../scripts/site-contract.mjs';
test('freeze human anchors, not renderer IDs', async () => {
  const html = '<main><h2 id="质量">质量</h2><h2 id="质量_1">质量</h2><span id=":R1:">live</span></main>';
  assert.deepEqual((await collectHeadingAnchors(html)).map(x => x.id), ['质量', '质量_1']);
});
```

- [ ] **Step 3: 实现注册表与捕获器。** 逐项录入规格中的 8 个研究 URL、7 个方法 URL，新增 `/research/` 和 `/data-sources/` 目录元信息；保留 `PUBLIC_ROUTES` 原键，新增 `research`、`docs`、`dataSources`、`search`。捕获器用已锁定 Playwright 的无脚本页面和 DOM 查询，整个 capture/check 会话复用一个浏览器，不为网站引入浏览器运行时。递归哈希只读取 `web/public/data`，相对路径稳定排序，文件内容不写入 fixture；check 同时比较源数据和 dist/data 的既有文件，证明发布复制未改变字节。新搜索索引放在 dist 根，不混入数据目录。
- [ ] **Step 4: 捕获真实旧站 fixture，并证明检测器有效。** 源码模块创建用 apply_patch；生成 fixture 使用受测的捕获命令属于机械产物。最终 fixture 只包含公开相对路径、章节和哈希。在 web 目录执行：

```bash
node scripts/site-contract.mjs capture dist tests/fixtures/legacy-site-contract.json tests/fixtures/public-snapshot-hashes.json
node scripts/site-contract.mjs check dist tests/fixtures/legacy-site-contract.json tests/fixtures/public-snapshot-hashes.json
node --import tsx --test src/public-registry.test.mjs src/site-contract.test.mjs src/routes.test.mjs
```

为临时合成站点添加测试：删去一个正文锚点、修改一个数据字节、删除一份数据，各自必须失败；只增加新章节允许通过。临时站点使用 `mkdtemp`，只清理其确切路径。旧真实 fixture 缺失或为空时失败，禁止后续用新站重新捕获来掩盖兼容问题。

- [ ] **Step 5: 提交。** `git diff --check`，仅暂存本任务列明的新文件与 routes 变更；提交 `test: freeze public routes anchors and snapshot contracts`。

## Task 2: 版本化因子定义与安全的因子链接

**Files:**

- Create: `web/src/content/factors.ts`
- Create: `web/src/content/factor-records.server.ts`
- Create: `web/src/lib/factor-links.ts`
- Create: `web/src/factor-records.test.mjs`
- Create: `web/src/factor-links.test.mjs`
- Modify: `web/src/components/react/style-page.tsx`（迁出静态字典，保持界面行为）
- Modify: `web/src/lib/factor-implementations.ts`（保留已有导出，引用关系不能成环）
- Modify: `web/package.json`、`web/package-lock.json`（把已有锁定的 `yaml@2.9.1` 声明为直接构建依赖）
- Read only: `studies/style_factors_18y/factor-descriptors.yml`、`web/public/data/barra/historical_factor_summary.json`。

**Interfaces:**

```ts
export type FactorRecord = {
  key: string; factorId: string; name: string; family: string;
  model: 'historical' | 'inspected' | 'core-proxy';
  version: string; source: string; direction: string;
  feature: string; calculation: string; caveats: readonly string[];
  verification: 'unverified' | 'source-inspected' | 'dictionary-defined';
};
// factors.ts: 19 项显式 ID/名称列表，历史方向和解释从现有 StylePage 搬出。
export const factorIds: readonly string[];
export function normalizeFactor(value: string | null): string;
// factor-records.server.ts: 读取明确的 YAML 文件，给 schema_version 加内容摘要。
export function readFactorRecords(): Promise<FactorRecord[]>;
// factor-links.ts: target 固定由调用方注册的站内 route 给出。
export function factorHref(target: string, factor: string | null, base: string, hash?: string): string;
```

`key = model + ':' + version + ':' + factorId`，历史版本使用来源包 ID，现行版本使用已核查完整 commit；核心代理使用 `schema-1:<字典文件内容摘要>`，不把 schema_version 误当作算法提交版本。浏览器只接收需要的记录，不导入 `.server.ts`、fs、YAML 解析器或内部文件路径。

- [ ] **Step 1: 写红测试并运行。** `cd web && node --import tsx --test src/factor-records.test.mjs src/factor-links.test.mjs`。

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFactorRecords } from './content/factor-records.server.ts';
test('same name never collapses different models', async () => {
  const records = await readFactorRecords();
  const sizes = records.filter(r => r.factorId === 'size');
  assert.equal(new Set(sizes.map(r => r.key)).size, 3);
  assert.equal(sizes.find(r => r.model === 'historical').verification, 'unverified');
  assert.equal(sizes.find(r => r.model === 'inspected').verification, 'source-inspected');
  assert.equal(sizes.find(r => r.model === 'core-proxy').verification, 'dictionary-defined');
  const quality = records.find(r => r.model === 'inspected' && r.factorId === 'quality');
  assert.match(quality.calculation, /8.*财务观测/);
  assert.match(quality.calculation, /至少 4/);
  assert.match(quality.calculation, /不保证.*连续季度/);
  assert.match(quality.calculation, /填 0/);
  assert.match(quality.calculation, /列整体缺失/);
});
```

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { factorHref } from './lib/factor-links.ts';
test('factor links use known values and the Pages base once', () => {
  assert.equal(factorHref('/docs/research/factors/barra-factor-dictionary/', 'quality', '/quant-market-research'),
    '/quant-market-research/docs/research/factors/barra-factor-dictionary/?factor=quality');
  assert.match(factorHref('/research/style-factors-18y/', 'toString', '/'), /factor=size$/);
  assert.match(factorHref('/research/style-factors-18y/', '__proto__', '/'), /factor=size$/);
});
```

- [ ] **Step 2: 迁出现有名称、方向、特征与对应关系，不改收益转换。** 把 `FACTOR_NAMES`、`FACTOR_DEFINITIONS`、`FACTOR_DETAILS` 移入 `factors.ts`，StylePage 从该文件导入。历史 method 文本只能标为旧页面记录，不自动提升为已核查历史公式。所有 19 个 ID 必须恰好一条历史记录，缺项／重复 key 抛出构建错误。
- [ ] **Step 3: 实现 server 适配和链接。** 声明已有 YAML 依赖 `npm install --save-dev --save-exact yaml@2.9.1`，确认 lock 只发生所需变更。`readFactorRecords` 逐家族展开 factors/composites，保持 transform、pit、direction 原值；用公开字段生成展示文案，不修改 YAML 或 Python 消费者。

```ts
// factors.ts
export function normalizeFactor(value: string | null): string {
  return value !== null && factorIds.includes(value) ? value : 'size';
}
// factor-links.ts（导入 normalizeFactor 和 withBase）
export function factorHref(target: string, factor: string | null, base: string, hash = ''): string {
  if (!target.startsWith('/') || target.startsWith('//') || target.includes('?') || target.includes('#')) {
    throw new Error('expected registered internal route');
  }
  const query = new URLSearchParams({factor: normalizeFactor(factor)});
  return `${withBase(target, base)}?${query}${hash ? '#' + encodeURIComponent(hash) : ''}`;
}
```

`factor-links.ts` 显式导入 `normalizeFactor` 和既有 `withBase`。Quality 核心字典仍标注“字典约定 8q，连续性及实际运行未核验”，现行实现为 8 财务观测最少 4；不把“字典定义存在”写成“历史已验证”。补充 size 方向相反、Beta 252/126、liquidity 形成日、liquidity_flow 仅列不存在才回退的逐项断言。

- [ ] **Step 4: 绿测试与既有交互回归。** 运行 `npm test`、`npm run build:pages`、`npm run e2e -- tests/e2e/barra-workbench.spec.ts`；确认依赖解析器不出现在客户端 bundle。执行任务 1 的 check 确认全部数据未改。
- [ ] **Step 5: 提交。** 仅暂存本任务文件，提交 `refactor: version public factor definitions without changing returns`。

## Task 3: 统一站点框架、目录、数据版本页与主题

**Files:**

- Modify: `docs/assets/theme-tokens.css`、`web/src/styles.css`、`web/src/theme.ts`
- Modify: `web/src/layouts/SiteLayout.astro`、`web/src/components/SiteHeader.astro`、`web/src/components/SiteFooter.astro`
- Modify: `web/src/components/ResearchPage.astro`、`web/src/components/ResearchOverview.tsx`
- Modify: `web/src/pages/index.astro`、`web/src/pages/404.astro`、`web/src/pages/research/factors/low-turnover/index.astro`
- Create: `web/src/pages/research/index.astro`、`web/src/pages/data-sources/index.astro`
- Create: `web/src/components/Breadcrumbs.astro`、`web/src/lib/data-catalog.ts`
- Create: `web/src/data-catalog.test.mjs`、`web/tests/e2e/unified-shell.spec.ts`
- Modify: `web/src/design-tokens.test.mjs`、`web/src/themeUi.test.mjs`、`web/src/astro-overview.test.mjs`、`web/tests/e2e/research-site.spec.ts`

**Interfaces:**

`SiteLayout` 保留原 title/description props，增加 `section?: SectionId`；旧 activeRoute 临时映射到 section，最终调用处直接使用 section。`workbench` 不再改变全站色彩。主区使用 `id="main-content"`，页头前有 skip link。

`Breadcrumbs` props 为 `items: readonly {label: string; href?: string}[]`；最后一项无 href、`aria-current="page"`。`snapshotCards(manifest: unknown): Array<{id:string; generatedAt:string|null; coverageStart:string|null; coverageEnd:string|null; status:string; source:string; caveats:string[]}>` 只投影 manifest 的公开字段；没有日期显示“未提供”，不使用构建日期补齐。

- [ ] **Step 1: 写红测试。** 新浏览器测试先验证非文档页共用壳，文档一致性留给任务 4；新纯函数测试固定 generated_at 不等于 coverage_end 的情况。

```ts
import {test, expect} from '@playwright/test';
test('one heading and a compact shared navigation', async ({page}) => {
  for (const route of ['./', 'research/', 'data-sources/', 'research/style-factors-18y/', '404.html']) {
    await page.goto(route);
    await expect(page.locator('main h1')).toHaveCount(1);
    await expect(page.locator('header h1')).toHaveCount(0);
    await expect(page.getByRole('navigation', {name: '主导航'})).toBeVisible();
    await expect(page.getByRole('link', {name: '方法与字典', exact: true})).toHaveAttribute('href', /\/docs\/$/);
  }
});
test('mobile navigation can be closed with Escape', async ({page}) => {
  await page.setViewportSize({width: 390, height: 844});
  await page.goto('./');
  const toggle = page.getByRole('button', {name: '展开主导航'});
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await page.keyboard.press('Escape');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(toggle).toBeFocused();
});
```

- [ ] **Step 2: 运行红测试。** `npm run build:pages && npm run e2e -- tests/e2e/unified-shell.spec.ts`；预期缺目录、h1 和菜单行为失败。记录失败点，再改代码。
- [ ] **Step 3: 实现公共框架和 tokens。** 使用紧凑品牌链接、四入口、主题控件；搜索入口在任务 8 路由可用后加入，不能先发布死链接。移动导航使用普通 disclosure，不伪装成需焦点陷阱的 modal；Escape 关闭后回到按钮，链接点击关闭，桌面宽度恢复菜单可见。没有 JS 时导航全部可访问。CSS 基础如下，并完整定义明暗 chart/semantic tokens：

```css
:root {
  --paper: #f7f8fa; --surface: #ffffff; --ink: #162233;
  --muted: #526174; --accent: #245da8; --rule: #d5dde7;
  --font-body: system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
  --font-heading: var(--font-body);
  --font-mono: ui-monospace, Consolas, monospace;
}
[data-theme="dark"] {
  --paper: #111820; --surface: #18222e; --ink: #edf2f7;
  --muted: #b4c0d0; --accent: #8ebcff; --rule: #3d4c60;
}
body { font: 1rem/1.7 var(--font-body); color: var(--ink); background: var(--paper); }
.site-main { width: min(100% - 2rem, 1240px); margin-inline: auto; }
.article-body { max-width: 46rem; margin-inline: auto; }
:where(h1,h2,h3,[id]) { scroll-margin-top: 6rem; }
:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
.table-scroll { max-width: 100%; overflow-x: auto; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
```

去掉 Google Fonts 导入和 `.research-workbench` 全局色板／字体覆盖，仍保留必要布局类。主题存储键仍为 `market-research-theme`；存储读写异常不会阻断菜单和渲染。修正语义标题：ResearchPage 标题 h1，OverviewContent 首标题 h1，其余为 h2/h3；低换手和 404 同样修正。为保留旧正文锚点，h2→h1 时不改已有 id。

- [ ] **Step 4: 填充可用目录和数据页。** 研究目录直接渲染注册表的 6 主题／8 研究页；首页保留有来源的发现，修正“Barra 内容却链接到指数”的入口。数据页只读取 `public/data/manifest.json`，展示生成／覆盖／质量状态／限制；将微盘主序列、repair、turnover 分行，未知日本日期不补造。添加测试：缺日期为 null、未知状态保留原文而不是“已验证”，非法 manifest 抛出明确错误。
- [ ] **Step 5: 绿测试和提交。** 更新旧 h2 断言为正文 h1，但保留原标题内容与直达刷新测试；运行 `npm test && npm run build:pages`、shell e2e、任务 1 check。提交 `feat: unify research shell navigation and source catalog`。此时旧 MkDocs 仍可用，任务 4 才切换其模板。

## Task 4: Astro 接管七份公开文档与发布流水线

**Files:**

- Create: `web/src/content.config.ts`、`web/src/content/public-docs-loader.ts`
- Create: `web/src/content/rehype-public-docs.ts`、`web/src/content/public-fragments.server.ts`
- Create: `web/src/content/legacy-anchor-map.ts`
- Create: `web/src/layouts/ArticleLayout.astro`、`web/src/pages/docs/[...slug].astro`
- Create: `web/src/public-docs.test.mjs`、`web/tests/e2e/public-docs.spec.ts`
- Modify: `web/astro.config.mjs`、`web/scripts/build-pages.mjs`、`web/scripts/verify-static-site.mjs`
- Modify: `web/package.json`、`web/package-lock.json`（仅增加构建期 Markdown processor）
- Modify: `web/src/build-pages.test.mjs`、`web/src/static-site-verifier.test.mjs`、`web/src/design-tokens.test.mjs`
- Modify: `mkdocs.yml`、`.gitignore`、`.github/workflows/pages.yml`、`AGENTS.md`、`README.md`
- Modify: `docs/index.md`、`docs/research/factors/barra-factor-dictionary.md`（其余五份只在必要链接／日期标签调整时修改）
- Read: 任务 1 的冻结锚点 fixture。

**Interfaces:**

```ts
// public-docs-loader.ts, only imported by content.config.ts
export function publicDocsLoader(): import('astro/loaders').Loader;
export function readPublicDocuments(repoRoot: string): Promise<Array<{meta: PublicDoc; body: string}>>;
// public-fragments.server.ts
export function expandPublicFragments(body: string, records: readonly FactorRecord[]): string;
// rehype-public-docs.ts
export function resolveDocLink(source: string, href: string, base: string): string;
export function publicDocsTransform(): (tree: unknown, file: unknown) => void;
```

`readPublicDocuments` 只打开注册表 7 个显式文件，检查 realpath 在 repo/docs 内且不是指向内部文件的符号链接；不 glob 整个 docs。文章 metadata 使用注册表，Markdown 不另复制 title/route。`publicDocsTransform` 为 Astro 的 rehype 插件，遍历 HAST 的 element.children；链接解析以 source 为基准，拒绝 `javascript:`、`data:`、内部 Markdown 与越界路径，普通 https/mailto 保留。`#章节` 和跨文章章节均保留并校验，重复 ID 直接失败。

- [ ] **Step 1: 写红测试，先保护白名单和链接。**

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveDocLink} from './content/rehype-public-docs.ts';
test('public markdown links keep the Pages base and encoded anchors', () => {
  assert.equal(resolveDocLink('docs/index.md', 'research/factors/microcap.md#先看风险', '/quant-market-research'),
    '/quant-market-research/docs/research/factors/microcap/#先看风险');
  assert.throws(() => resolveDocLink('docs/index.md', 'superpowers/specs/internal.md', '/'), /public|allowlist/i);
  assert.throws(() => resolveDocLink('docs/index.md', '../../private.md', '/'), /outside|public/i);
});
```

另用临时 repo 创建 7 个允许文件和 `docs/internal.md`（正文 `INTERNAL_ONLY_SENTINEL`）；断言读取结果只有 7 项且不含 sentinel，删一个允许文件必须失败。浏览器测试请求七个 URL，检查 `main h1`、`主导航`、公开正文、UTF-8/NUL；使用旧 fixture 逐个比较 id，中文 percent-encoded fragment 也要滚动到真实正文。

- [ ] **Step 2a: 运行红测试，并配置锁定版本所需的 Markdown processor。** 当前 Astro 7.3.2 默认使用 Sätteri；rehype 插件不能假设像旧 Astro 一样直接生效。执行 `npm install --save-dev --save-exact @astrojs/markdown-remark@7.3.1`，只增加构建期依赖，不升级 Astro/React 或加入 MDX。该版本已通过 npm 元数据查询核实；安装后按类型和构建测试验证导出。

```js
// astro.config.mjs 的新增 imports 和 markdown 属性；其余既有配置保留。
import {unified, rehypeHeadingIds} from '@astrojs/markdown-remark';
import {publicDocsTransform} from './src/content/rehype-public-docs.ts';
const publicMarkdown = unified({rehypePlugins: [rehypeHeadingIds, publicDocsTransform]});
// 在原有 defineConfig 对象中加入：markdown: {processor: publicMarkdown}
```

Astro 自带 processor 是唯一公开 Markdown 渲染链，不同时再用另一渲染器生成相同正文。增加构建断言：正文 ID、`render()` headings 和 qmrSearchSections 的链接全部一致，以实测确认插件顺序。

- [ ] **Step 2b: 实现白名单 loader。** 关键代码如下；导入的函数均在本任务或前置任务定义：

```ts
import type {Loader} from 'astro/loaders';
import {fileURLToPath} from 'node:url';
import {readFactorRecords} from './factor-records.server';
import {expandPublicFragments} from './public-fragments.server';
export function publicDocsLoader(): Loader {
  return {
    name: 'reviewed-public-documents',
    async load({config, store, parseData, renderMarkdown}) {
      const root = new URL('../', config.root);
      const documents = await readPublicDocuments(fileURLToPath(root));
      const records = await readFactorRecords();
      store.clear();
      for (const {meta, body} of documents) {
        const expanded = expandPublicFragments(body, records);
        const data = await parseData({id: meta.id, data: meta});
        const rendered = await renderMarkdown(expanded, {fileURL: new URL(meta.source, root)});
        store.set({id: meta.id, data, body: expanded, rendered});
      }
    },
  };
}
```

`content.config.ts` 使用 `defineCollection({loader: publicDocsLoader()})` 和完整 registry metadata schema，导出 `publicDocs` collection。`[...slug].astro` 用 `getCollection` 和 `render`，slug 为空时 params 为 `undefined`，生成 `/docs/`；`ArticleLayout` 不再额外输出 h1，直接使用正文已有 h1。目录来自同一 rendered headings，避免两套 slugger。开发模式监听七个白名单文件和字典；有变化重新执行相同加载函数，不扩大可读取范围，避免静默保留旧正文。

插件完成 heading/link 变换后，用同一 HAST 遍历收集 `{id:string; title:string; text:string}` 章节；排除 script/style、导航和兼容空 span。写入 `file.data.astro.frontmatter.qmrSearchSections`，由 renderMarkdown 返回的 `rendered.metadata.frontmatter` 保存；任务 8 只消费这些已渲染正文记录，不再次解析 Markdown。用构建测试确认七篇文章均有该字段，缺少时明确失败。所有插入片段都必须先通过此处理再进入搜索。`/docs/` 首页同时列出注册表全部七份说明，保留已有正文和旧锚点，不只保留原来的三个链接。

- [ ] **Step 3: 插入公共片段、保留锚点与阅读路径。** 将字典重复公式表替换为显式 `<!-- qmr:core-proxy -->`、`<!-- qmr:inspected-factors -->`、`<!-- qmr:historical-factors -->` 标记，`expandPublicFragments` 由相同 FactorRecord 生成 Markdown 表／段落；代码内联值和表格竖线正确转义。保留解释、历史日期和来源不足说明，不把日期旧的状态报告改成实时状态。未知 marker 构建失败。MkDocs 参考预览可显示“结构化定义见公开字典”链接，不再维护一套手抄公式。

`legacy-anchor-map.ts` 显式保存旧章节 ID 到新章节 ID 的对应关系，值取任务 1 真实输出而不是猜 slug。标题不变时尽量直接沿用旧 ID；重命名时在对应章节开头加兼容 span，不能把所有别名集中放页顶。对移除的重复表格，将旧章节锚点放到接替它的定义区。兼容别名无重复、滚动偏移有效。

- [ ] **Step 4: 同一次提交切换构建和门禁。** `mkdocs.yml` 的 site_dir 改为 `.build/mkdocs-reference` 并 gitignore；`build-pages.mjs` 依次 Astro build、MkDocs strict reference、写 `.nojekyll`、verify。Pages CI 调用 `npm run build:pages`，保留 Python、Ruff、资源报告、浏览器和隐私扫描；删除 Bootstrap 专有资源断言的同时增加 7 个 Astro 文档输出、旧锚点、跨页链接与正文检查，不删除安全断言。保留已有 React alias 原样。

```js
// build-pages.mjs 中保留既有 run()；MkDocs 的输出目录由新 mkdocs.yml 限定。
run(npm, ['run', 'build'], web);
run(uv, ['run', '--locked', '--extra', 'docs', 'mkdocs', 'build', '--strict'], root);
writeFileSync(path.join(web, 'dist', '.nojekyll'), '');
run(npm, ['run', 'verify:static'], web);
```

构建测试改为检查真实产物和参考输出位置，不能只删除旧源码正则。静态 verifier 对所有站内 href 校验文件和 fragment，合并兼容 alias；对指向纯 React 延迟章节的链接由浏览器断言补充，不能误判为无锚点后关闭全部 fragment 检查。内部路径／secret marker 的扫描继续覆盖 HTML、JS、JSON、CSV、CSS。

- [ ] **Step 5: 绿测试、文档与提交。** `npm test && npm run build:pages`，运行 public-docs e2e、任务 1 check；构建内部 sentinel 样例并确认 dist 全文和所有客户端产物无 sentinel。README／AGENTS 的步骤改为统一 build:pages，明确 MkDocs 不发布。提交 `feat: serve reviewed documentation through Astro`。

## Task 5: 共享图表容器、配色与可访问数值入口

**Files:**

- Create: `web/src/lib/chart-presentation.ts`
- Create: `web/src/components/ChartFrame.astro`、`web/src/components/react/ChartFrame.tsx`
- Create: `web/src/chart-presentation.test.mjs`
- Modify: `web/src/components/ResearchCharts.tsx`、`web/src/components/react/research-shared.tsx`
- Modify: `web/src/theme.ts`、`web/src/styles.css`、`web/src/chart-values.test.mjs`

**Interfaces:**

```ts
export type ChartMeta = {
  id: string; title: string; unit: string; sample: string;
  boundary: string; explanation: string; methodHref?: string;
};
export type ChartFrameProps = ChartMeta & {children: React.ReactNode; data?: React.ReactNode};
export function chartLabel(value: number | null, unit: 'percent' | 'number'): string;
export function baseChartOptions(theme: {axis:string; grid:string; label:string; tooltip:string},
  reducedMotion: boolean): import('echarts').EChartsOption;
```

Astro ChartFrame 同样接收 ChartMeta，默认 slot 为图，`data` slot 为数值；两者输出同名 `.chart-frame` 类和 `aria-labelledby`，不各自携带一份 CSS。React 包装器不会创建嵌套 `.panel`，原 Panel 仍用于非图表模块。

- [ ] **Step 1: 红测试固定缺失与零、动效、说明。**

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import {chartLabel, baseChartOptions} from './lib/chart-presentation.ts';
test('missing is not zero and reduced motion is honored', () => {
  assert.equal(chartLabel(null, 'percent'), '未提供');
  assert.equal(chartLabel(0, 'percent'), '0.0%');
  assert.equal(chartLabel(-0.02, 'percent'), '-2.0%');
  const option = baseChartOptions({axis:'#526174',grid:'#d5dde7',label:'#162233',tooltip:'#ffffff'}, true);
  assert.equal(option.animation, false);
  assert.equal(option.textStyle.fontSize, 12);
});
```

使用 React server renderer 的现有测试方式验证 ChartFrame 输出包含单位、样本、局限、读图说明、方法链接和数值 details；Astro 外壳在任务 7 的低换手实际页断言覆盖。

- [ ] **Step 2: 运行红测试。** `node --import tsx --test src/chart-presentation.test.mjs src/chart-values.test.mjs`。
- [ ] **Step 3: 实现公共显示逻辑。** 保持传入百分比为小数，不二次缩放历史 annual_ret（它由现有调用端除以 100）；非有限值显示缺失。统一 ECharts tooltip 背景／边框／文本、坐标字体和网格，响应主题变化与 reduced-motion。BarChart 保留零线和负号，LineChart 保留缩放和 null 间断，不擅自改变既有统计或平滑设置。默认单序列色从语义 token 取得，不能靠一组专题 hex 值覆盖深色模式。

```ts
export function chartLabel(value: number | null, unit: 'percent' | 'number'): string {
  if (value === null || !Number.isFinite(value)) return '未提供';
  return unit === 'percent' ? `${(value * 100).toFixed(1)}%` : value.toLocaleString('zh-CN');
}
```

图表容器的标题和读图说明始终静态可见；Canvas 失败仍有数值入口。可滚动大表提供可见说明和键盘焦点，不给每个单元格添加 tabIndex。

- [ ] **Step 4: 运行图表、theme、format 和资源测试，完整 build。** 确认 0/null/负值、logScale 非正值回退、主题刷新和 chart dispose 仍正确。任务 6、7 才逐页采用外壳，本任务不修改研究样本或 API。
- [ ] **Step 5: 提交。** `refactor: share accessible chart presentation primitives`。

## Task 6: Barra 图表、定义与方法文章联动

**Files:**

- Modify: `web/src/pages/research/style-factors-18y/index.astro`
- Modify: `web/src/components/react/style-page.tsx`、`web/src/content/factors.ts`
- Create: `web/src/components/react/FactorDetails.tsx`
- Create: `web/src/components/FactorContextLink.astro`
- Modify: `web/src/layouts/ArticleLayout.astro`、`web/tests/e2e/barra-workbench.spec.ts`
- Modify: `web/tests/e2e/research-site.spec.ts`
- Remove only if imports are zero: `web/src/components/research/BarraFactorDictionary.astro`（已被共享内容替代的静态重复表）。

**Interfaces:**

`StylePage` props 扩展为 `{scope: StyleScope; factorRecords?: readonly FactorRecord[]}`；Astro 页面在构建期 `readFactorRecords()` 并仅传公开记录。`FactorDetails({factorId, records})` 按 model/version 分组，显示相同 ID 的三个证据层，不在每次选择时重新抓取原始数据。`FactorContextLink` props `{target:string; label:string; base:string; hash?:string}`，SSR 默认 size 链接，轻量脚本只把合法当前 factor 写入固定 target，禁止接受任意 return URL。

- [ ] **Step 1: 增加红测试。**

```ts
import {test, expect} from '@playwright/test';
test('selected factor survives methodology round trip and history', async ({page}) => {
  await page.goto('research/style-factors-18y/?factor=quality');
  await page.getByRole('link', {name: '阅读完整因子定义', exact: true}).click();
  await expect(page).toHaveURL(/barra-factor-dictionary\/\?factor=quality/);
  await page.getByRole('link', {name: '回到因子图表', exact: true}).click();
  await expect(page.locator('button[data-factor="quality"]')).toHaveAttribute('aria-pressed', 'true');
  await page.goBack();
  await expect(page).toHaveURL(/barra-factor-dictionary\/\?factor=quality/);
  await page.goForward();
  await expect(page.locator('button[data-factor="quality"]')).toHaveAttribute('aria-pressed', 'true');
});
```

追加 size 历史／核心方向不同、Quality 的 8 观测与 8q 标签不同的文本断言；任意 factor、`constructor`、空值均回到 size、不抛 pageerror。保留现有 19 因子、503重试、延迟加载、每页 50 条及 ARIA ID 测试。

- [ ] **Step 2: 运行红测试。** `npm run build:pages && npm run e2e -- tests/e2e/barra-workbench.spec.ts`。
- [ ] **Step 3: 采用 ChartFrame 和 FactorDetails。** 保留 `barra-annual`、`barra-factor-detail`、`barra-overview`、`barra-correlations` ID。主图后显示选中因子定义，Quality 四子项仅选择 Quality 时显示；版本限制常驻，不放进折叠深处。公共历史摘要和百分比转换继续用原代码。因子选择保持现有 replaceState 语义（不为每次点击堆积历史），跨页往返和 popstate 根据 URL 恢复。

```tsx
<FactorDetails factorId={selectedFactor} records={factorRecords} />
<a href={factorHref('/docs/research/factors/barra-factor-dictionary/', selectedFactor, base)}>
  阅读完整因子定义
</a>
```

StylePage 内显式取得 `base = import.meta.env.BASE_URL ?? '/'`；缺少 factorRecords 只允许 indices 模式，Barra 构建必须提供，避免静默空定义。删除只用于重复字典的旧 JSX 和无引用 Astro 表格前用 `rg` 确认消费者。

- [ ] **Step 4: 绿测试。** 两份现有 e2e 全跑，保留 Quality 已有 1.2%／10.5%、样本范围与表格分页断言；新增数值期望必须从冻结数据推导，不凭记忆填写。运行任务 1 check 和 factor-records 测试。
- [ ] **Step 5: 提交。** `feat: connect factor charts definitions and methodology`。

## Task 7: 全部非 Barra 专题采用阅读模板并补齐失败恢复

**Files:**

- Create: `web/src/components/TopicNav.astro`、`web/src/lib/topic-sections.ts`
- Modify: `web/src/components/ResearchPage.astro`
- Modify: `web/src/pages/research/cashflow/index.astro`、`web/src/pages/research/cashflow/recovery/index.astro`
- Modify: `web/src/pages/research/microcap/index.astro`、`web/src/pages/research/microcap/cross-market-liquidity/index.astro`
- Modify: `web/src/pages/research/indices/index.astro`、`web/src/pages/research/liquidity/index.astro`、`web/src/pages/research/factors/low-turnover/index.astro`
- Modify: `web/src/components/react/cashflow-page.tsx`、`web/src/components/react/microcap-page.tsx`、`web/src/components/react/liquidity-page.tsx`、`web/src/components/react/style-page.tsx`（IndicesPage）
- Modify as needed for the same contract: `web/src/components/MicrocapCharts.tsx`、`web/src/components/RecoverySection.tsx`、`web/src/components/ReplicationSection.tsx`、`web/src/components/LowTurnoverExecutionEvidence.tsx`
- Create: `web/tests/e2e/topic-reading.spec.ts`、`web/src/topic-sections.test.mjs`

**Interfaces:**

`TopicSection = {id:string; label:string; available:boolean}`；`visibleSections(sections: readonly TopicSection[]): TopicSection[]` 排除无内容项。`TopicNav` 只生成真正存在的锚点，名称为“本页目录”。ResearchPage 的统一头部仅展示问题、短结论、必要日期与核心局限；完整 FreshnessStrip/ResearchContext 放到数据方法区，不能让解释所必需的风险随之折叠。

- [ ] **Step 1: 写红测试，按专题枚举恢复行为。** 对下面四个已核实的主请求补失败和成功重试，不使用匹配所有请求的宽拦截。client:visible 岛屿先滚动进入可见范围。

```ts
import {test, expect} from '@playwright/test';
for (const [route, dataset, island] of [
  ['research/indices/', 'index/linked_indices/ten_year_price_returns.csv', 'StylePage'],
  ['research/cashflow/', 'index/cashflow_indices/cashflow_performance.csv', 'CashflowPage'],
  ['research/microcap/', 'index/microcap/summary.json', 'MicrocapPage'],
  ['research/liquidity/', 'liquidity/summary.json', 'LiquidityPage'],
] as const) {
  test(`${route} recovers from a required dataset failure`, async ({page}) => {
    let fail = true;
    await page.route(`**/data/${dataset}`, handler =>
      fail ? handler.fulfill({status:503, body:'unavailable'}) : handler.continue());
    await page.goto(route);
    await page.locator(`astro-island[component-export="${island}"]`).scrollIntoViewIfNeeded();
    await expect(page.getByRole('alert').first()).toContainText('加载失败');
    fail = false;
    const count = await page.getByRole('alert').count();
    for (let remaining = count; remaining > 0; remaining--) {
      await page.getByRole('alert').first().getByRole('button', {name: /重试/}).click();
      await expect(page.getByRole('alert')).toHaveCount(remaining - 1);
    }
    await expect(page.locator('canvas').first()).toBeVisible();
  });
}
```

成功但空数据应显示暂无数据，不能无限 Loading。Quality 可选请求已有任务 6 的回归。低换手数字、方法链接、共同 86 个月与 1 个月前瞻限制必须仍可见。再增加现金流的第二请求 cashflow_rebalance_frequency.csv 失败测试，证明并非只修了第一个资源。

- [ ] **Step 2: 运行红测试。** `npm run build:pages && npm run e2e -- tests/e2e/topic-reading.spec.ts`。
- [ ] **Step 3: 调整各页内容顺序和图表外壳。** 七个路由逐个按照“问题／短结论→主图→读图→定义／方法→数据与局限”适配；去掉 React 子页与 Astro 外壳重复的主题大标题，不删说明。低换手报告条形图保留 HTML 图形和现有数据，仅用 Astro ChartFrame 包围；图表数字、单位和表格数值一致，不改变排序口径。各页添加相应方法文章或真实同页章节的返回链接；没有独立长文的指数／流动性不生成虚假方法页。
- [ ] **Step 4: 按资源状态显式分支。** 使用已有 ResourceState/useJson/useCsv；可选资源失败不阻断主图。多个必需资源失败时显示各自标签与 retry，不能只给最后一个请求重试。

```tsx
const summary = useJson<LiquiditySummary>('liquidity/summary.json');
if (summary.error) return <ResourceState label="流动性研究" error={summary.error} retry={summary.retry}/>;
if (summary.loading) return <ResourceState label="流动性研究" loading/>;
if (!summary.data) return <ResourceState label="流动性研究" empty/>;
```

保留上述已存在的 path，不能为配合界面重命名或移动公开快照。对合法空的 markets 数组显示空状态，坏结构用解析验证抛出可重试错误；其他请求按自身数据契约区分空与坏数据。保留供应商指数／规则重建、价格／全收益、strict／partial／carry 分类；不合并不同样本曲线来追求美观。

- [ ] **Step 5: 绿测试和提交。** 运行全部前端测试、build:pages、topic-reading 和 research-site e2e、冻结数据 check。每个路由检查正文 h1 唯一、标题层级和二级导航目标存在。提交 `feat: align research topics and recover failed data loads`。

## Task 8: 公开内容搜索与安全、轻量的索引

**Files:**

- Create: `web/src/lib/search.ts`、`web/src/content/search-records.server.ts`
- Create: `web/src/pages/search/index.astro`、`web/src/pages/search-index.json.ts`
- Create: `web/src/components/react/SearchResults.tsx`
- Create: `web/src/search.test.mjs`、`web/tests/e2e/search.spec.ts`
- Modify: `web/src/components/SiteHeader.astro`、`web/scripts/verify-static-site.mjs`
- Modify: `web/src/styles.css`、`web/scripts/report-bundle-size.mjs`

**Interfaces:**

```ts
export type SearchRecord = {
  id:string; title:string; kind:'research'|'method'|'factor'|'data';
  href:string; text:string; aliases:readonly string[];
};
export function normalizeQuery(value:string): string;
export function searchRecords(records:readonly SearchRecord[], query:string): SearchRecord[];
export function buildSearchRecords(): Promise<SearchRecord[]>;
```

`href` 带站点 base 和精确章节；关键词来自公开注册表、已展开的七份正文、版本化因子定义与数据页公开说明。研究摘要从 registry，不导入 React 页面或 ECharts。方法全文使用任务 4 的 `entry.rendered.metadata.frontmatter.qmrSearchSections`，验证数组及字段后生成记录；不单独读整个 docs。搜索结果不注入任意 HTML，标题／snippet 由 React 文本节点输出。

- [ ] **Step 1: 写红测试。**

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import {searchRecords} from './lib/search.ts';
const items = [{id:'quality',title:'复合质量',kind:'factor',href:'/quant-market-research/research/style-factors-18y/?factor=quality#barra-factor-detail',text:'ROE 及盈利稳定性；现行源码，不代表历史公式',aliases:['quality','质量']}];
test('Chinese and English search are normalized and never invent results', () => {
  assert.deepEqual(searchRecords(items, '盈利稳定'), items);
  assert.deepEqual(searchRecords(items, '  QUALITY  '), items);
  assert.deepEqual(searchRecords(items, '不存在的指标'), []);
  assert.deepEqual(searchRecords(items, '   '), []);
  assert.deepEqual(searchRecords(items, '<script>alert(1)</script>'), []);
});
```

增加实际索引边界测试：7 份文章都有结果入口、不含内部 sentinel/规格文件名/绝对路径；JSON UTF-8 字节数 ≤250*1024。浏览器测试搜索失败 503→重试成功、无结果、直接 `?q=quality`、中英文因子点击和后退恢复查询。

- [ ] **Step 2: 运行红测试。** `node --import tsx --test src/search.test.mjs`，新索引路由完成前 e2e 应失败。
- [ ] **Step 3: 实现确定性检索和静态 endpoint。** trim + NFKC + lowerCase，多个空白分词按 AND 匹配；完整中文片段使用 includes，标题／别名匹配优先，随后正文，再按稳定 id 排序。空查询显示提示和目录链接，超长查询截到 200 Unicode code points。searchRecords 返回完整排序结果；组件显示 `matches.slice(0, 30)` 和“前 30 / 总数 matches.length”，不能伪装为全量展示。

```ts
export function normalizeQuery(value: string): string {
  return Array.from(value.normalize('NFKC').trim().toLowerCase()).slice(0, 200).join('');
}
```

`search-index.json.ts` 静态 GET 只调用 buildSearchRecords，显式 `Content-Type: application/json; charset=utf-8`；构建超过体积阈值报错。片段按章节切分，重复导航不入索引；不截去定义限制文字只保留漂亮结论。查询不发送第三方，首页／文章只提供普通 GET 搜索表单，不请求索引。SearchResults 用现有资源状态机制或同等取消／重试逻辑，响应 URL 的 q 和 popstate。

- [ ] **Step 4: 加搜索入口和无 JS 后备。** Header 增加“搜索”链接；搜索页保留服务器生成的目录链接与说明。将搜索页加入构建路由检查，但不索引它自己的结果正文。查询提交后更新 `?q=`，不通过静态 Astro SSR 读取不存在的运行时 query；客户端初始化从 window.location 读取。加载索引前不显示“没有结果”，失效 JSON 不能当作空数组。
- [ ] **Step 5: 绿测试与提交。** `npm test && npm run build:pages && npm run e2e -- tests/e2e/search.spec.ts`；记录索引真实体积和网络请求，核查方法页／首页没有 ECharts、size CSV、search-index 请求。提交 `feat: search reviewed research and versioned definitions`。

## Task 9: 全站视觉、可访问性、兼容与性能验收

**Files:**

- Create: `web/tests/e2e/unified-experience.spec.ts`
- Create: `web/tests/e2e/helpers/contrast.ts`
- Create: `docs/superpowers/reviews/2026-09-19-unified-research-experience.md`
- Modify: 前述页面／样式／测试中实际发现问题的文件；每个修复补最小失败用例。
- Do not publish: `web/test-results`、review 文档、trace 和本地截图。

**Interfaces:** `contrastRatio(foreground: string, background: string): number` 接收浏览器 computed RGB，使用 WCAG 相对亮度公式；带 alpha 时先与实际父背景合成再计算。视觉证据矩阵以 route × viewport × theme 标识，记录截图路径、检查人/代理、发现和修复，不能只写“截图已生成”。

- [ ] **Step 1: 写整站行为与布局断言。** 每个公开页均执行无全局溢出、h1、nav 当前状态和控制台错误检查；代表截图为至少 5 个规定页面 × 桌面/手机 × 明/暗共 20 个组合，再加入方法目录、数据和搜索的关键状态，不用固定截图张数代替规格范围。

```ts
import {test, expect} from '@playwright/test';
for (const width of [320, 390, 768, 1280, 1440]) {
  test(`unified layout at ${width}`, async ({page}) => {
    await page.setViewportSize({width,height:900});
    for (const route of ['./','research/style-factors-18y/','research/factors/low-turnover/','research/microcap/','docs/research/factors/barra-factor-dictionary/']) {
      await page.goto(route);
      await expect(page.locator('main h1')).toHaveCount(1);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBeTruthy();
    }
  });
}
test('blocked storage does not prevent navigation or readable content', async ({page}) => {
  await page.addInitScript(() => {
    Storage.prototype.getItem = () => {throw new DOMException('blocked','SecurityError');};
    Storage.prototype.setItem = () => {throw new DOMException('blocked','SecurityError');};
  });
  await page.emulateMedia({colorScheme:'dark',reducedMotion:'reduce'});
  await page.goto('./');
  await expect(page.locator('main h1')).toBeVisible();
  await page.getByRole('link', {name:'方法与字典', exact:true}).click();
  await expect(page.locator('main h1')).toBeVisible();
});
```

为正常存储增加 light/dark/system 的跨页面持久化及系统变化测试；禁用存储时采用系统偏好且无异常，无法持久化要优雅降级。增加按 Tab 访问 skip link／菜单／搜索／因子／表格排序与分页，focus 可见；同页锚点不被 sticky header 挡住。

- [ ] **Step 2: 执行矩阵并实际看图。** 必看首页、Barra、低换手、微盘和长方法文章的桌面/手机×明/暗共至少 20 个组合，余下全部路由巡检。检查主图是否被重复介绍挤到下方、定义是否贴近图表、密集表格是否可读、长标题/数字是否断行、nav/header/文章是否同风格、颜色对比。用实际浏览器工具和 `view_image` 检视；浏览器工具不可用时可查看 Playwright 截图，但不能虚报真实点击验收已做。
- [ ] **Step 3: 网络与失败矩阵。** 首页和方法页观察到的请求不得包含 ECharts chunk、研究 CSV 或 search-index；Barra 初始不能抓市值十分组，展开一次请求一次；索引只在搜索时抓。观察客户端构建依赖图确认 YAML/fs 不入 bundle。断网／503/坏 JSON/空数组时显示可理解状态和适当重试，测试因子快速切换不会用过期响应覆盖选择。
- [ ] **Step 4: 完整新验证，记录实际结果。**

```bash
uv run --locked --extra duckdb --extra dev pytest -q
uv run --locked --extra dev ruff check src tests scripts
(cd web && npm test && npm run build:pages && npm run report:bundle && npm run e2e)
(cd web && node scripts/site-contract.mjs check dist tests/fixtures/legacy-site-contract.json tests/fixtures/public-snapshot-hashes.json)
git diff af5b8b9cf8d7075325b1a0e9617465956bded1d4 --exit-code -- web/public/data
git diff --check
```

baseline commit 仅用于确认本改版未改已有研究数据；如果执行前已整合 main 上合法的数据变更，则使用已审查的新执行基线，绝不能把他人的变化回滚。记录所有新增测试数、bundle/index 大小、覆盖路径和未解决事项，不照抄上轮结果。

- [ ] **Step 5: 自审修复后提交验收记录。** `test: verify unified site compatibility accessibility and performance`。请求独立整分支审查；若当前环境无独立 reviewer，明确报告并保留 PR 等待审查，不把本人的自审当作独立审查。

## Task 10: PR、部署核验与仅本任务的清理

**Files:** 仅按审查修正实现／测试及更新非公开验收记录，不新增功能。

**Interfaces:** 输入为用户批准的实施计划、独立审查结果和本地验证记录；输出为 PR 地址、merge SHA、部署 URL、线上检查证据、剩余研究限制和任务工作树清理记录。

- [ ] **Step 1: 检查提交范围。** `git status --short`、`git diff --stat origin/main...HEAD`、`git log --oneline origin/main..HEAD`；没有其他任务内容或未保存修改。PR 不包含原始行情、凭证、内部数据产物；设计／计划可以提交仓库但不能进入 Pages。
- [ ] **Step 2: 推送任务分支并建 PR。** 使用既有 gh/Git 凭据；网络失败按用户规则有界重试。不要因为一次失败就读 token，不打印 token 或修改用户持久配置。PR 正文说明 7 文档迁移、旧链接合约、19 因子版本边界、测试/截图与数据哈希不变。不同执行模式可保留规划分支或在同一已隔离 worktree 中更名为 feature 分支；不在共享 main 开发。
- [ ] **Step 3: 等待并处理检查和审查。** 必需检查全部成功、无冲突、独立审查意见已处理才合并。没有审查能力或权限则保留已推 PR 并说明缺项；不以“用户说全部推进”绕过仓库门禁。
- [ ] **Step 4: 合并后等待 Pages 成功并核验真实 URL。** 检查首页、Barra `?factor=quality` 往返、低换手、长方法页、至少一个中文旧深链接、搜索、主题、404、manifest 与已发布快照哈希、原始 HTML 的 UTF-8/NUL。线上版本应对应 merge SHA，失败时不删除分支/工作树。
- [ ] **Step 5: 需要回滚时走明确恢复流程。** 优先重新部署前一份已验证 Pages artifact；若无该 artifact，则创建 revert PR 并按 CI/审查合并。禁止 force push、删数据或手改 production 目录；与修复路径冲突时报告并请用户决定。
- [ ] **Step 6: 仅清理本任务。** 确认合并提交存在、工作树干净、没有只存在于临时路径的未保存截图／记录后，先保留用户需要的证据副本，再删除任务远端分支、正规 `git worktree remove <已核实本任务绝对路径>`、最后删除本地分支。主检出干净时 `git pull --ff-only`。不得清理其他 Codex 的 worktree。最终交付 PR、部署、测试、cleanup 和历史来源／PIT 未解决限制。

## 规格覆盖与计划自查

| 规格范围 | 落实任务 |
| --- | --- |
| 导航、所有 URL 与历史锚点 | 1、3、4、6、9 |
| 三类模板、字体配色、主题、标题结构 | 3、4、5、7、9 |
| 图表优先、19 因子、Quality 四子项 | 2、5、6 |
| 同源定义与历史/现行/代理分层 | 2、4、6 |
| 7 文档白名单、单一生成器、隐私 | 1、4、8、9 |
| 数据目录、日期、不可变数值 | 1、3、7、9 |
| 搜索、空状态、错误恢复、性能 | 5、6、7、8、9 |
| 移动、深浅色、键盘、真实视觉检查 | 3、9 |
| CI、独立审查、PR、发布、回滚、清理 | 4、9、10 |

计划审阅时特别确认：实施仍不包括恢复历史 19 因子生成版本、补齐 PIT、重算 Quality 或改变市值收益缺失政策。这些是独立研究工作，不以界面迁移名义宣称解决。

技术 API 依据：[Astro 内容集合](https://docs.astro.build/en/guides/content-collections/)用于构建期内容路由；[Astro Content Loader API](https://docs.astro.build/en/reference/content-loader-reference/)用于白名单 loader 与 renderMarkdown；[Markdown processor 配置](https://docs.astro.build/en/reference/configuration-reference/#markdownprocessor)和[插件元信息](https://docs.astro.build/en/guides/markdown-content/#modifying-frontmatter-programmatically)用于公开正文变换与索引。Astro 7 的 processor 差异也已在当前安装源码中核对。执行时以锁定版本的类型和测试为准，不升级框架来迁就示例。

## 执行方式交接（待用户选择）

推荐 Native：由当前代理按任务顺序实施，每项做红绿测试和小提交，最后进行独立整分支审查。本计划共享注册表、布局、因子模型和发布链路较多，顺序实施能减少接口冲突。

另一方式为 Subagent-driven：每个任务独立 implementer 和 reviewer，接口稳定后再开始下一项，最后整分支审查；更细致但上下文成本更高。当前会话未发现原生子代理派发工具，选择此方式需先确认可用执行环境，不承诺已经具备独立代理审查。

用户确认本计划及执行方式后才开始任务 1；本次规划提交不安装产品依赖、不修改网站代码、不合并 main 或部署。
