# 公开研究网站迁移到 Astro 的设计

## 背景

`quant-market-research` 同时维护 Python 研究代码、公开网页和 MkDocs 说明站。研究计算和公开数据快照已经分离，网页使用 Vite、React、TypeScript 和 ECharts，说明站使用 MkDocs 并发布到 `/docs/`。

当前网页以一个 React 应用呈现所有研究主题。`web/src/main.tsx` 集中了页面选择、数据读取、页面内容和交互状态，站内导航依赖 URL hash。现有 React 页面和图表已有测试及公开数据约定，继续使用它们可以降低迁移风险。主页和说明页也分别维护 CSS，基础颜色、字体和版式变量存在重复。

用户已确认采用 Astro 作为公开网页的长期方向，保留 React/ECharts 交互、保留 MkDocs 文档站，并分阶段实施。

## 目标

将公开研究网页逐步迁移为 Astro 静态多页面站。每个研究主题都有可直接访问、可刷新和可分享的 URL。页面标题、研究摘要、方法和风险说明以静态 HTML 输出。图表、筛选器和可排序表格继续由 React/ECharts 提供交互。

统一主页和说明站的基础设计变量，让颜色、字体、边框和常用尺寸有单一来源。两类页面的布局样式仍按各自结构维护。

保留 GitHub Pages 静态部署、`/docs/` 地址、现有公开数据文件及其 JSON/CSV 字段。不得将原始行情、研究运行目录、私有 alpha、凭证或内部手册发布到站点。

## 方案

### 采用：Astro 页面路由，React 交互岛

Astro 负责网站路由、共享布局、静态 HTML 生成和资源构建。React 继续用于现有图表、筛选器、可排序表格等交互模块，ECharts 保持不变。页面按主题拆分，构建后只加载当前路由所需的交互代码。

将公共颜色、字体和基础尺寸整理为一份共享 CSS 变量文件。Vite/Astro 构建导入这份文件，MkDocs 继续从 `docs/assets/` 加载它。主页与说明站的页面布局和组件样式保留各自文件，避免把不同 HTML 结构强行合并成一份样式表。

### 暂不采用：仅抽共享变量，继续单页应用

该方案改动较小，但仍保留 hash 路由和集中式页面组件，不能解决每个研究主题独立访问、静态正文输出及路由级代码拆分的问题。可作为不迁移框架时的退路。

### 暂不采用：Astro 同时接管文档

Astro + Starlight 可以进一步统一网站和说明站，但当前 MkDocs 已稳定发布，公开页面数量有限，并且内部文档依赖明确的发布白名单。现在迁移会同时改变网站框架和文档构建，扩大回归面。等公开文档规模或维护需求明显增加后，再单独评估。

## 架构与数据流

```text
本地或受控研究数据
        │
        ▼
Python 研究代码和审核后的派生结果
        │
        ▼
web/public/data 中的公开 JSON/CSV 快照
        │
        ├── Astro：静态页面、路由、共享站点布局
        └── React/ECharts：图表、过滤、排序等交互

Astro 构建 web/dist
        │
        ├── MkDocs 构建 web/dist/docs
        └── GitHub Pages 发布 web/dist
```

数据文件继续按现有路径和结构读取。路由迁移不改研究计算、数据 schema、快照生成器或数据刷新流程。浏览器所需的资源和数据 URL 必须以 Astro 配置的站点基础路径生成，适配 GitHub Pages 的 `/quant-market-research/` 子路径。

Astro 页面负责可静态确定的标题、描述、方法、解释和风险提示。React 组件负责必须在浏览器交互的数据图表与控件。页面首屏应在 JavaScript 执行前包含有意义的研究标题和边界说明。ECharts 初始化及需要浏览器 API 的代码不得在静态构建时访问 `window` 或 `document`。

## 页面路由和兼容性

每个公开研究主题使用独立、稳定的小写 URL。实施计划应将现有有效 hash 全部映射到新路由，并为遗留链接保留轻量跳转。推荐路由如下：

| 页面 | 新 URL | 现有 hash |
| --- | --- | --- |
| 研究总览 | `/` | `#overview` 或空 hash |
| 现金流研究 | `/research/cashflow/` | `#cashflow` |
| 现金流恢复研究 | `/research/cashflow/recovery/` | `#cashflow-recovery` 跳转到新页的 `#cashflow-recovery` 区块 |
| 微盘研究 | `/research/microcap/` | `#microcap` |
| 微盘回本与持有期研究 | `/research/microcap/#microcap-recovery` | `#microcap-recovery` |
| 微盘跨市场流动性 | `/research/microcap/cross-market-liquidity/` | `#cross-market` |
| 市场指数 | `/research/indices/` | `#style`、`#indices` |
| 风格因子研究 | `/research/style-factors-18y/` | `#style-factors-18y` |
| 流动性研究 | `/research/liquidity/` | `#liquidity` |

实施前应核对 `main.tsx` 和组件中的锚点、导航文案与页面状态，确认表中的旧 hash 含义。若旧链接代表页面内区块，应跳转到新页面的对应区块；若只代表页面，应跳转到页面根部。不得让旧 hash 失效或意外落在总览页。

现有说明站继续使用 `https://runchengxie.github.io/quant-market-research/docs/`，原 MkDocs 构建顺序和公开文档白名单保持有效。README 中网页与说明站的链接继续可用。

## 设计变量

共享 CSS 文件作为基础视觉变量的唯一来源，至少包含：

- 页面底色、内容底色、正文颜色和辅助文字颜色
- 强调色、浅强调色、分隔线颜色
- 正文、衬线标题和等宽辅助文字的字体栈
- 常用内容宽度及基础圆角/边框约定

暗色主题变量若由主页继续支持，应在主页主题层覆写共享变量，不改变 MkDocs 当前的浅色阅读体验。图表系列颜色等研究图形配置仍由图表组件管理。

## 构建和发布

Astro 构建输出仍为 `web/dist/`。随后 MkDocs 构建到 `web/dist/docs/`，不得清空 Astro 页面或资源。CI 保留 Python 测试与 Ruff 检查，增加 Astro 类型/构建检查，并保留 MkDocs strict 构建、公开资源存在检查、`.nojekyll` 处理和公共产物敏感路径/凭证标记扫描。

所有路由必须由静态构建生成，GitHub Pages 无需运行时服务器、API 服务或重写规则。相对资源和页面数据路径必须覆盖本地预览与 GitHub Pages 子路径两种环境。

## 安全与研究边界

- 仅从 `web/public/data/` 等已审核的公开快照读取数据。
- 不把 `outputs/`、原始行情、完整研究运行结果或 `docs/` 中未公开的操作手册复制到 Astro 公共目录。
- 保留当前产物扫描，并检查 Astro 新的 HTML、JS、CSS 和 source map 输出。
- 数据来源或质量待核实的页面继续显示现有状态标签、口径说明和风险提示。
- 此迁移不修改收益、风险、回撤或因子分析的计算结果。

## 分阶段实施

## 当前实现记录

本轮已完成 Astro 静态多页面入口、共享站点外壳、正式研究 URL、旧 hash 兼容、GitHub Pages 子路径数据访问、MkDocs 共享设计变量、构建产物检查和浏览器冒烟测试。主页摘要由 Astro 在构建时读取公开快照并生成静态 HTML。

当前各研究页仍由 `ResearchRoutes.tsx` 统一承载，Astro 页面输出独立标题、摘要和研究边界，再加载该 React 路由组件呈现专题主体。图表及部分数据组件按需加载，但研究正文尚未逐页迁成静态 Astro 内容，React bundle 也尚未做到路由级拆分。因此本轮实现了可分享的静态路由和站点框架，尚未达到目标中完整的正文静态化和每页独立交互代码加载。后续应按访问量和维护优先级逐页拆分，不应将现状描述为零 JavaScript 或已完成路由级代码拆分。

### 阶段一：站点底座

在独立分支验证 Astro 与现有 Vite/React、GitHub Pages 子路径、共享 CSS 变量及 MkDocs 顺序构建的共存方式。先建立最小入口、全局布局和构建验收，不改变公开页面内容或数据契约。阶段产物须能以一个静态目录预览并通过现有公开产物扫描。

### 阶段二：多页面和组件拆分

按研究主题逐页迁移。把页面路由/布局和交互数据组件拆开，复用现有 React/ECharts 组件，形成路由级加载。每批页面都保留旧 hash 跳转并验证直接访问、刷新、导航、图表、数据加载和窄屏布局。

### 阶段三：切换入口和清理旧壳

所有已列页面均迁移并通过验收后，将 Astro 首页设为正式入口，移除 Vite 单页壳和只服务于旧 hash 路由的状态。核验旧 URL、MkDocs `/docs/`、主题切换、公开数据路径和 GitHub Pages 部署。

### 后续独立工作：Python 公开快照发布

将公开快照转换、schema 校验、字段规范化和隐私检查评估为单独改造。它与 Astro 路由迁移使用同一公开数据契约，但不在此次网页框架迁移中同时改变。当前 Node 快照脚本中存在简单的逗号分隔解析逻辑，后续可改由 Python 标准 CSV 读取器或既有 pandas 流程处理，并用引号、逗号、换行等合法 CSV 样例验证。

### 后续独立评估：Starlight

MkDocs 继续维护 `/docs/`。只有当公开文档、导航或复用需求增加时，再评估 Astro + Starlight，并单独处理迁移、搜索能力和 URL 兼容。

## 验收标准

1. 当前每个研究主题拥有可直接访问的静态 URL，刷新和复制链接后仍能打开正确页面。
2. 现有有效 hash 有兼容跳转，导航不依赖一个巨型 React 根组件进行页面切换。
3. 公开页面首屏包含静态标题、简述和研究边界。交互图表、筛选和可排序表格仍可正常使用。
4. 浏览器只加载当前页面所需的研究交互代码；具体 bundle 大小只作为实测结果，不预设提升幅度。
5. `/docs/` 的页面、CSS、脚本、字体和搜索资源完整，内容白名单仍生效。
6. 构建产物保持纯静态，并通过密钥标记、本机路径、内部路径和原始数据边界检查。
7. Python 研究计算、公开 JSON/CSV 结构和现有报告输出保持不变。
8. PR CI 通过 Python、Ruff、Web 单元测试、Astro 检查/构建、MkDocs strict 构建及产物扫描。

## 不在本次范围内

- 把 MkDocs 迁移到 Starlight。
- 重写 Python 数据分析、策略或因子收益计算。
- 同时升级 React 大版本或更换 ECharts。
- 引入服务器运行时、API、登录系统或数据库服务。
- 因框架迁移改写研究结论或公开数据 schema。
- 承诺或预先宣称性能提升，性能变化以构建产物和浏览器实测为准。
