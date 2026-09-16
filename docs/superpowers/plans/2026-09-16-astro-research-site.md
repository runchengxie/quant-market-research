# Astro 研究网站迁移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将公开研究网页迁移为 Astro 静态多页面站，保留 React/ECharts 交互、MkDocs 说明站、GitHub Pages 地址和公开数据契约。

**Architecture:** Astro 提供正式路由、公共页面框架和静态首页摘要。现有研究主体暂由共享 React 路由组件承载，交互组件保留 React/ECharts。主页和 MkDocs 共用 CSS 设计变量。Astro 先输出到 `web/dist/`，随后 MkDocs 写入 `web/dist/docs/`。逐页静态化正文和路由级交互代码拆分列为后续工作。

**Tech Stack:** Astro、`@astrojs/react`、React 18、TypeScript、ECharts、MkDocs、GitHub Actions、Node.js test runner；路由验收使用 Playwright。

**Spec:** `docs/superpowers/specs/2026-09-16-astro-research-site-design.md`

## Global Constraints

- Python 研究代码、研究计算和数据刷新流程保持不变。
- `web/public/data/` 中已审核的公开 JSON/CSV 路径和字段保持不变。
- 静态站部署到 `https://runchengxie.github.io/quant-market-research/`，支持 GitHub Pages 子路径。
- MkDocs 继续发布到 `/docs/`，只输出白名单中的公开说明页和必要资源。
- 不发布 `outputs/`、原始数据、内部手册、本机路径或凭证。
- 所有新路由须能直接访问、刷新和复制分享，旧 hash 入口须跳转到对应路由或区块。
- 不升级 React 大版本，不替换 ECharts，不引入服务端运行时。
- 每个路线迁移保留适用的现有数据状态提示、来源口径和研究限制。

---

## 文件职责

- `web/astro.config.mjs`：静态输出、站点 URL、GitHub Pages 基础路径和 React 集成。
- `web/src/pages/`：Astro 文件路由和每页静态标题、摘要及研究边界。
- `web/src/layouts/SiteLayout.astro`：统一的站点标题、Meta、导航、页脚和主题启动脚本。
- `web/src/components/react/`：从 `main.tsx` 拆出的交互页面、图表和控件。
- `web/src/lib/public-data.ts`：公开数据 URL、CSV/JSON 读取与显示格式化工具。
- `web/src/lib/routes.ts`：正式路由表和旧 hash 兼容表。
- `docs/assets/theme-tokens.css`：主页和 MkDocs 共用的基础设计变量。
- `web/scripts/verify-static-site.mjs`：构建后检查路由、资源、MkDocs 输出和公开内容边界。
- `web/tests/e2e/`：直接访问、页面刷新、页面导航和交互的 Playwright 冒烟测试。
- `.github/workflows/pages.yml`：执行 Astro、Web、Python 和 MkDocs 检查并发布同一静态目录。

---

### Task 1：加入 Astro 构建底座

**Files:**
- Modify: `web/package.json`
- Modify: `web/package-lock.json`
- Create: `web/astro.config.mjs`
- Create: `web/src/pages/index.astro`
- Create: `web/src/env.d.ts`
- Modify: `web/tsconfig.json`

**Interfaces:**
- Astro 将 `web/src/pages/` 编译到 `web/dist/`。
- React 集成允许 Astro 页面导入 `.tsx` 组件。
- GitHub Pages 配置使用 `site: "https://runchengxie.github.io"` 和 `base: "/quant-market-research"`。

- [x] **Step 1：先加构建配置测试**

在 `web/src/astro-config.test.mjs` 检查配置中的静态输出、站点地址、base 和 React 集成名称：

```js
assert.match(config, /output:\s*["']static["']/);
assert.match(config, /base:\s*["']\/quant-market-research["']/);
assert.match(config, /react\(\)/);
```

- [x] **Step 2：运行测试确认当前配置失败**

运行：`cd web && npm test -- --test-name-pattern="Astro build configuration"`

预期：新测试因缺少 `astro.config.mjs` 失败。

- [x] **Step 3：安装稳定版 Astro 和 React 集成并建立入口**

运行：`cd web && npm install --save-dev astro @astrojs/react @astrojs/check`

将脚本更新为：

```json
"dev": "astro dev",
"check": "astro check",
"build": "astro check && astro build",
"preview": "astro preview"
```

配置文件使用：

```js
export default defineConfig({
  site: "https://runchengxie.github.io",
  base: "/quant-market-research",
  output: "static",
  integrations: [react()],
  outDir: "./dist",
});
```

更新 `tsconfig.json` 使用 Astro 推荐配置并保留 `strict: true`、`jsx: "react-jsx"`。首页先输出站点名和简短研究站说明，不挂载旧 React 总应用。

- [x] **Step 4：验证 Astro 静态构建**

运行：`cd web && npm test && npm run build`

预期：`web/dist/index.html` 存在，包含站点标题和正确的仓库 base 资源路径。

- [ ] **Step 5：提交**

运行：

```bash
git add web/package.json web/package-lock.json web/astro.config.mjs web/src/pages/index.astro web/src/env.d.ts web/src/astro-config.test.mjs
git commit -m "build: add Astro static site foundation"
```

### Task 2：统一共享设计变量和站点外壳

**Files:**
- Create: `docs/assets/theme-tokens.css`
- Create: `web/src/layouts/SiteLayout.astro`
- Create: `web/src/components/SiteHeader.astro`
- Create: `web/src/components/SiteFooter.astro`
- Create: `web/src/components/react/ThemeToggle.tsx`
- Modify: `web/src/styles.css`
- Modify: `docs/assets/docs.css`
- Modify: `mkdocs.yml`
- Test: `web/src/design-tokens.test.mjs`

**Interfaces:**
- `theme-tokens.css` 定义 `--paper`、`--surface`、`--ink`、`--muted`、`--rule`、`--accent`、`--accent-soft` 及 `--font-body`、`--font-heading`、`--font-mono`。
- `SiteLayout.astro` 接受 `title`、`description`、`activeRoute` 和页面内容 slot。
- `ThemeToggle.tsx` 继续使用 `web/src/theme.ts` 的 `ThemeChoice`、`readThemeChoice`、`persistThemeChoice` 和 `applyTheme`。

- [x] **Step 1：写共享变量契约测试**

检查主页和说明站样式都引用唯一 tokens 文件，且该文件声明设计说明中列出的变量。测试还要确保 `mkdocs.yml` 的 `extra_css` 加载 token 文件。

- [x] **Step 2：运行测试确认共享文件尚不存在**

运行：`cd web && npm test -- --test-name-pattern="shared design tokens"`

预期：测试因共享文件不存在失败。

- [x] **Step 3：抽取变量并建立 Astro 布局**

将首页和 `docs/assets/docs.css` 重复的浅色变量与字体栈移入 `docs/assets/theme-tokens.css`。主页通过相对 CSS import 加载同一文件，必要时仅为开发服务器配置仓库根目录的 `server.fs.allow`。MkDocs 先加载 `assets/theme-tokens.css`，再加载 `assets/docs.css`，并在 `exclude_docs` 精确放行 token 文件。主页暗色调色板继续在主题选择层覆写共享变量。页面 CSS 继续只定义自身布局。`SiteLayout.astro` 输出主页同款 Header/Footer 结构和每页 Meta。

- [x] **Step 4：验证主题测试及两套构建**

运行：

```bash
cd web && npm test && npm run build
cd .. && uv run --locked --extra docs mkdocs build --strict
```

预期：Astro 和 MkDocs 输出均包含共享变量，亮色视觉变量一致，MkDocs 深色阅读没有被主页主题切换影响。

- [ ] **Step 5：提交**

运行：`git add docs/assets web/src mkdocs.yml && git commit -m "style: share public site design tokens"`

### Task 3：定义正式路由和旧 hash 跳转

**Files:**
- Create: `web/src/lib/routes.ts`
- Create: `web/src/routes.test.mjs`
- Create: `web/src/components/LegacyHashRedirect.astro`
- Modify: `web/src/components/SiteHeader.astro`
- Modify: `web/src/components/SiteFooter.astro`
- Modify: `web/src/components/ResearchOverview.tsx`
- Modify: `web/src/components/RecoverySection.tsx`

**Interfaces:**
- `PUBLIC_ROUTES` 保存总览和七个研究路由。
- `LEGACY_HASH_ROUTES` 将现有 hash 映射到绝对站内路径，可包含目标区块 hash。
- `withBase(path, baseUrl)` 负责加入 `/quant-market-research/`，不产生双斜线或重复 base。
- `LegacyHashRedirect.astro` 只在命中兼容表时调用 `location.replace()`。

路由纯函数接口固定为：

```ts
export const PUBLIC_ROUTES = {
  overview: "/",
  cashflow: "/research/cashflow/",
  cashflowRecovery: "/research/cashflow/recovery/",
  microcap: "/research/microcap/",
  crossMarketLiquidity: "/research/microcap/cross-market-liquidity/",
  indices: "/research/indices/",
  styleFactors: "/research/style-factors-18y/",
  liquidity: "/research/liquidity/",
} as const;

export function withBase(path: string, baseUrl: string): string {
  const base = baseUrl === "/" ? "" : baseUrl.replace(/\/$/, "");
  return `${base}/${path.replace(/^\//, "")}`;
}

export const LEGACY_HASH_ROUTES = {
  "": PUBLIC_ROUTES.overview,
  "#overview": PUBLIC_ROUTES.overview,
  "#cashflow": PUBLIC_ROUTES.cashflow,
  "#cashflow-recovery": `${PUBLIC_ROUTES.cashflowRecovery}#cashflow-recovery`,
  "#microcap": PUBLIC_ROUTES.microcap,
  "#microcap-recovery": `${PUBLIC_ROUTES.microcap}#microcap-recovery`,
  "#cross-market": PUBLIC_ROUTES.crossMarketLiquidity,
  "#style": PUBLIC_ROUTES.indices,
  "#indices": PUBLIC_ROUTES.indices,
  "#style-factors-18y": PUBLIC_ROUTES.styleFactors,
  "#liquidity": PUBLIC_ROUTES.liquidity,
} as const;
```

路由至少包含：`/`、`/research/cashflow/`、`/research/cashflow/recovery/`、`/research/microcap/`、`/research/microcap/cross-market-liquidity/`、`/research/indices/`、`/research/style-factors-18y/` 和 `/research/liquidity/`。

- [ ] **Step 1：测试正式 URL、每个有效旧 hash 和 base 拼接**

测试覆盖空 hash、`overview`、`cashflow`、`cashflow-recovery`、`microcap`、`microcap-recovery`、`cross-market`、`style`、`style-factors-18y`、`indices` 和 `liquidity`。base 拼接测试使用：

```js
assert.equal(
  withBase("/research/microcap/", "/quant-market-research/"),
  "/quant-market-research/research/microcap/",
);
assert.equal(withBase("/", "/"), "/");
```

- [ ] **Step 2：运行测试确认路由表失败**

运行：`cd web && npm test -- --test-name-pattern="public route compatibility"`

预期：因路由模块缺失失败。

- [ ] **Step 3：实现路由和兼容组件**

用纯数据对象表示映射。首页只处理本地已存在的旧 hash，不解析或重定向外站 URL。更新首页卡片、恢复期交叉链接和导航为正式路径。

- [ ] **Step 4：验证路由表和首页链接**

运行：`cd web && npm test`

预期：旧 hash 映射无遗漏，内部导航不再生成新的 `href="#cashflow"` 等 hash 链接。

- [ ] **Step 5：提交**

运行：`git add web/src && git commit -m "feat: define public research routes"`

### Task 4：迁移总览页并生成静态研究正文

**Files:**
- Modify: `web/src/pages/index.astro`
- Create: `web/src/lib/public-data.ts`
- Modify: `web/src/components/ResearchOverview.tsx`
- Modify: `web/src/overview.test.mjs`
- Create: `web/src/index-page.test.mjs`

**Interfaces:**
- `readPublicJson<T>(relativePath)` 在 Astro 构建期从 `web/public/data/` 读取已审核 JSON，并在缺失或 JSON 无效时返回可见的 unavailable 状态。
- 总览页使用现有 `OverviewContent` 生成静态 HTML，不为静态内容添加 `client:*` 指令。

- [ ] **Step 1：增加总览构建输出测试**

构建后检查 `dist/index.html` 含研究总览标题、当前研究状态、至少一个内部 `/research/.../` 链接，以及指向 `/quant-market-research/docs/` 的说明链接。

- [ ] **Step 2：先运行输出测试确认失败**

运行：`cd web && npm run build && node --test src/index-page.test.mjs`

预期：当前占位首页缺少预期研究正文，测试失败。

- [ ] **Step 3：接入审核过的总览数据和现有总览组件**

使用构建期 JSON loader 读取现有 recovery 与 Barra 摘要。保留组件对缺失数据、质量状态和研究边界的既有处理。把 `<OverviewContent>` 作为服务端静态 React 输出，不启用浏览器 hydration。

- [ ] **Step 4：验证页面内容无需 JavaScript 即可读取**

运行：`cd web && npm test && npm run build && node --test src/index-page.test.mjs`

预期：页面源 HTML 已包含标题、研究范围、数据状态和内部正式路径。

- [ ] **Step 5：提交**

运行：`git add web/src && git commit -m "feat: render research overview with Astro"`

### Task 5：拆分共享 React 控件与公开数据读取

**Files:**
- Create: `web/src/lib/public-data-client.ts`
- Create: `web/src/lib/format.ts`
- Create: `web/src/components/react/shared/ResearchUi.tsx`
- Create: `web/src/public-data-client.test.mjs`
- Modify: `web/src/components/RecoverySection.tsx`
- Modify: `web/src/components/ResearchCharts.tsx`
- Modify: `web/src/components/MicrocapCharts.tsx`
- Modify: `web/src/main.tsx`

**Interfaces:**
- `publicDataUrl(path, baseUrl)` 将 `data/...` 拼到 Astro base 下。
- `usePublicJson<T>(path)`、`usePublicCsv(path)` 保留现有 loading/error 状态并支持取消请求。
- `ResearchUi.tsx` 导出 `Stat`、`Panel`、`ThemeHeading`、`ControlBar`、`Choice`、`SimpleTable` 和 `SortableTable`。

- [ ] **Step 1：增加子路径 URL 与格式化回归测试**

测试 `/`、`/quant-market-research/` 和尾斜线输入，确保 JSON/CSV URL 不落在深层页面目录下。

- [ ] **Step 2：运行测试确认辅助模块缺失**

运行：`cd web && npm test -- --test-name-pattern="public data URL"`

预期：模块导入失败。

- [ ] **Step 3：提取共用实现并迁移现有组件调用**

将 CSV 的引号、转义双引号、逗号、CRLF 和空行行为保留到独立 parser。React 页面只调用 `publicDataUrl`，禁止继续拼接 `./data/...` 相对路径。将重复 UI 和数值格式化函数从 `main.tsx` 移出。

- [ ] **Step 4：验证数据边界和现有组件测试**

运行：`cd web && npm test && npm run build`

预期：既有快照校验、missing 与真实零值测试通过，新增 URL/parser 测试通过。

- [ ] **Step 5：提交**

运行：`git add web/src && git commit -m "refactor: extract public data and research UI helpers"`

### Task 6：迁移现金流和恢复期页面

**Files:**
- Create: `web/src/pages/research/cashflow/index.astro`
- Create: `web/src/pages/research/cashflow/recovery/index.astro`
- Create: `web/src/components/react/pages/CashflowDashboard.tsx`
- Create: `web/src/components/react/pages/RecoveryDashboard.tsx`
- Create: `web/src/cashflow-routes.test.mjs`
- Modify: `web/src/main.tsx`
- Modify: `web/src/components/ReplicationSection.tsx`
- Modify: `web/src/components/RecoverySection.tsx`

**Interfaces:**
- `CashflowDashboard` 渲染现有现金流回报、调仓频率、复制对照和恢复期交互。
- `RecoveryDashboard` 接收 `scope: "cashflow" | "microcap"`，保留现有恢复快照校验和缺失状态。

- [ ] **Step 1：写两条现金流页的构建产物测试**

构建后分别检查页面标题、静态数据边界说明、恢复区块 id 和对应静态资源引用。

- [ ] **Step 2：运行测试确认路由尚不存在**

运行：`cd web && npm run build && node --test src/cashflow-routes.test.mjs`

预期：两个路由页面不存在，测试失败。

- [ ] **Step 3：提取现金流页面和恢复组件**

把 `CashflowPage` 与 `CashflowPageContent` 移入 `CashflowDashboard.tsx`。使用共享数据 URL helper。Astro 页静态输出标题、研究摘要和状态边界，交互部分以 React island 加载。恢复期页面保留 `cashflow-recovery` anchor。

- [ ] **Step 4：检查现金流和恢复交互**

运行：`cd web && npm test && npm run build && node --test src/cashflow-routes.test.mjs`

预期：直接构建的两个页面存在，样本口径和 unavailable 状态测试保持通过。

- [ ] **Step 5：提交**

运行：`git add web/src && git commit -m "feat: add cashflow research routes"`

### Task 7：迁移微盘、回撤和跨市场页面

**Files:**
- Create: `web/src/pages/research/microcap/index.astro`
- Create: `web/src/pages/research/microcap/cross-market-liquidity/index.astro`
- Create: `web/src/components/react/pages/MicrocapDashboard.tsx`
- Create: `web/src/components/react/pages/CrossMarketLiquidityDashboard.tsx`
- Create: `web/src/microcap-routes.test.mjs`
- Modify: `web/src/main.tsx`
- Modify: `web/src/components/MicrocapCharts.tsx`
- Modify: `web/src/components/RecoverySection.tsx`
- Modify: `web/src/components/ReplicationSection.tsx`

**Interfaces:**
- `MicrocapDashboard` 接收 `initialSection?: "recovery"`，支持微盘恢复期旧 hash 锚点。
- `CrossMarketLiquidityDashboard` 渲染跨市场流动性研究，沿用现有摘要和完整性标签。

- [ ] **Step 1：写微盘静态输出和 data URL 测试**

断言两个路由包含正确标题、重建数据边界和 `microcap-recovery` anchor。检查所有被引用数据文件由 base path 生成。

- [ ] **Step 2：运行测试确认目标输出不存在**

运行：`cd web && npm run build && node --test src/microcap-routes.test.mjs`

预期：目标 HTML 缺失，测试失败。

- [ ] **Step 3：迁移微盘与跨市场交互组件**

保留净值、收益、回撤和恢复区间图表组件及原字段映射。Astro 静态区块包含页面标题和未核实提示。图表使用 viewport 触发的 island，首屏必要控件按交互时序加载。旧 recovery hash 映射到该页实际区块。

- [ ] **Step 4：验证 N、样本日期和风险提示未改动**

运行：`cd web && npm test && npm run build && node --test src/microcap-routes.test.mjs`

预期：公开快照边界测试通过，两个页面均能生成静态 HTML。

- [ ] **Step 5：提交**

运行：`git add web/src && git commit -m "feat: add microcap research routes"`

### Task 8：迁移风格、指数和流动性页面

**Files:**
- Create: `web/src/pages/research/indices/index.astro`
- Create: `web/src/pages/research/style-factors-18y/index.astro`
- Create: `web/src/pages/research/liquidity/index.astro`
- Create: `web/src/components/react/pages/IndicesDashboard.tsx`
- Create: `web/src/components/react/pages/StyleFactorsDashboard.tsx`
- Create: `web/src/components/react/pages/LiquidityDashboard.tsx`
- Create: `web/src/style-and-liquidity-routes.test.mjs`
- Modify: `web/src/main.tsx`
- Modify: `web/src/components/ResearchCharts.tsx`

**Interfaces:**
- 每个 Astro 页包含独立 title、description、canonical route 和静态研究边界。
- `StyleFactorsDashboard` 保留 Barra 摘要、因子选择、逐年收益及相关性数据检查。
- `LiquidityDashboard` 保留日期、市场和指标选择状态。

- [ ] **Step 1：写三条研究页输出测试**

测试目标页的 title、各自可见的来源/时间范围提示和正式 route links。

- [ ] **Step 2：运行测试确认路由失败**

运行：`cd web && npm run build && node --test src/style-and-liquidity-routes.test.mjs`

预期：至少一个目标页面缺失导致失败。

- [ ] **Step 3：分别提取页面组件和 Astro 页**

从旧总应用中迁移 `IndicesPage`、`BarraPage` 和 `LiquidityPage` 及各自必需的数据类型。旧 `#style`、`#indices` 跳至指数页，`#style-factors-18y` 跳至风格因子页。所有数据通过共享读取模块。

- [ ] **Step 4：运行 Web 测试和 Astro 构建**

运行：`cd web && npm test && npm run build && node --test src/style-and-liquidity-routes.test.mjs`

预期：三个路由均生成，单个页面不再带入其他研究页的数据模块。

- [ ] **Step 5：提交**

运行：`git add web/src && git commit -m "feat: add style and liquidity research routes"`

### Task 9：删除旧单页路由并保持链接兼容

**Files:**
- Modify: `web/src/pages/index.astro`
- Create: `web/src/pages/404.astro`
- Modify: `web/src/routes.test.mjs`
- Modify: `web/src/components/LegacyHashRedirect.astro`
- Modify: `web/src/components/ResearchOverview.tsx`
- Modify: `web/src/components/RecoverySection.tsx`
- Modify: `web/src/editorialUi.test.mjs`
- Modify: `web/src/themeUi.test.mjs`
- Delete: `web/src/main.tsx`
- Delete: `web/index.html`
- Delete: `web/vite.config.ts`

**Interfaces:**
- 首页 hash shim 仅执行旧 hash 到正式 route 的映射。
- 未知路径输出有用的本地 404 页面，并提供首页和研究页入口。

- [ ] **Step 1：更新所有现存链接和路由回归测试**

测试扫描输出 HTML 的本地锚点，确保旧顶级 hash 不再作为主要导航链接出现，并逐一验证遗留 hash 映射。

- [ ] **Step 2：运行测试确认无效内部引用可被检测**

运行：`cd web && npm test`

预期：未改写的总览或恢复页旧 hash 链接会导致新测试失败。

- [ ] **Step 3：移除旧 root app 并添加 404**

逐个移出旧页面后，删除已无 import 的单页入口与 Vite 配置。保留所需纯函数和测试。404 页面使用 `SiteLayout.astro`，不依赖浏览器路由重写。

- [ ] **Step 4：验证正式导航、旧 hash 和 404**

运行：`cd web && npm test && npm run build`

预期：所有正式链接是根相对且带 Pages base 的路径，legacy hash 定向跳转，`404.html` 不含旧 React SPA 根节点。

- [ ] **Step 5：提交**

运行：`git add -A web && git commit -m "refactor: replace hash navigation with Astro routes"`

### Task 10：迁移构建流水线并验证公开产物

**Files:**
- Create: `web/scripts/verify-static-site.mjs`
- Modify: `web/package.json`
- Modify: `.github/workflows/pages.yml`
- Modify: `tests/test_quality.py`
- Modify: `docs/runbook-local.md`

**Interfaces:**
- `npm run verify:site` 验证静态路由列表、Astro base、共享 CSS、旧 hash shim、MkDocs CSS/JS/字体/搜索资源和 `.nojekyll`。
- Pages workflow 顺序固定为 `npm ci`、`npm test`、`npm run build`、`touch dist/.nojekyll`、`mkdocs build --strict`、`npm run verify:site`、公开产物扫描。

- [ ] **Step 1：先写静态产物和 CI 顺序测试**

测试需要从 `web/dist/` 逐项读取路由 `index.html`，确保 CSS、JS 和 JSON 路径在 Pages base 下有效。Python 测试确保 MkDocs 输出目录仍为 `web/dist/docs` 且 whitelist 包含共享 tokens。CI 测试确保 MkDocs 在 Astro build 之后运行。

- [ ] **Step 2：用当前产物运行验证器测试并确认失败**

运行：`cd web && npm run build && npm run verify:site`

预期：在完整路由、MkDocs 合并构建和验证脚本实现前，验证器测试失败。

- [ ] **Step 3：实现验证器并更新 Actions**

验证器拒绝缺失路由、丢失 docs 资源、路径越界、缺 `.nojekyll` 和泄露标记。Actions 保持现有 Python pytest、Ruff、Docs 构建和 Pages artifact 权限。

- [ ] **Step 4：运行仓库完整质量门禁**

运行：

```bash
uv run --locked --extra duckdb --extra dev pytest -q
uv run --locked --extra dev ruff check src tests scripts
cd web && npm ci && npm test && npm run build && npm run verify:site
cd .. && uv run --locked --extra docs mkdocs build --strict
git diff --check
```

预期：所有命令通过，公开产物只包含审核过的数据快照和白名单文档。

- [ ] **Step 5：提交**

运行：`git add .github/workflows/pages.yml tests/test_quality.py docs/runbook-local.md web && git commit -m "ci: verify Astro and MkDocs Pages output"`

### Task 11：增加浏览器冒烟测试并核对部署

**Files:**
- Modify: `web/package.json`
- Modify: `web/package-lock.json`
- Create: `web/playwright.config.ts`
- Create: `web/tests/e2e/research-pages.spec.ts`
- Modify: `.github/workflows/pages.yml`

**Interfaces:**
- Playwright preview 从 `web/dist/` 提供页面。
- 冒烟测试覆盖首页、所有正式 route、至少一个 ECharts 页面、恢复期交叉导航、主题切换和 `/docs/`。

- [ ] **Step 1：添加关键用户路径测试**

测试用 `page.goto()` 直接打开至少 `/research/microcap/`、`/research/cashflow/recovery/` 和 `/docs/`；刷新后验证页面标题仍存在；点击一个目录/导航链接验证目标；图表页等待图表容器和数据状态完成。

- [ ] **Step 2：运行 Playwright 测试确认迁移入口未满足路径**

运行：`cd web && npm run test:e2e`

预期：在 browser automation 未接线前因脚本或浏览器入口失败。

- [ ] **Step 3：安装 Playwright Chromium 并配置 preview server**

使用 `@playwright/test` 和 `webServer.command: "npm run preview -- --host 127.0.0.1"`。本地/CI 只安装 Chromium，不安装未使用的浏览器。

- [ ] **Step 4：在 CI 和本地运行冒烟测试**

运行：`cd web && npx playwright install --with-deps chromium && npm run test:e2e`

预期：所有页面可直接打开、刷新、导航和显示图表，不出现控制台页面级异常。

- [ ] **Step 5：合并后的 Pages 发布核验**

PR CI 通过后合并到 `main`，等待 Pages workflow 成功。访问项目主页、代表性研究路由和 `/docs/`，确认 HTTP 200、CSS/JS/数据资源 HTTP 200、页面版本更新。随后清理本任务的远端分支、本地分支和 worktree，并快进同步主工作树。

运行：`git add web/package.json web/package-lock.json web/playwright.config.ts web/tests/e2e .github/workflows/pages.yml && git commit -m "test: smoke test published research routes"`

## 迁移完成后的后续工作

- 单独建立 Python 公开快照发布计划，替换 `web/scripts/build-public-snapshot.mjs` 的简单 CSV 分割器，固定 JSON schema 并增加公开字段审查。
- 等公开文档规模增长后，再单独比较 MkDocs 与 Starlight 的迁移成本。
- 比较迁移前后的首屏 JS、页面 HTML 大小和图表加载时机，只记录实测值，不预设收益。

## 本轮实施说明

本轮实际完成了 Astro 静态多页面入口、正式路由和旧 hash 兼容、共享站点框架与设计变量、主页公开快照静态摘要、MkDocs 顺序构建、静态产物检查和 Playwright 冒烟测试。研究专题主体仍由 `web/src/components/react/ResearchRoutes.tsx` 统一分发，因此不满足原计划中的逐页 Astro 正文和路由级 bundle 拆分目标。后续按专题将静态解释内容迁入 Astro，并把图表与筛选拆成独立交互组件。此计划用于记录已执行方案及尚存差距，原步骤中的文件名和命令仅在与当前实现一致时作为参考。
