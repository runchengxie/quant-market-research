# Astro-first 页面架构设计

## 目标

把网站整理成 Astro-first 的静态研究站。Astro 负责 URL、页面布局、研究正文和静态内容，React 只负责需要浏览器状态的图表、筛选、搜索、排序和主题切换。

## 现状

Astro 已经负责页面路由和 SiteLayout，但研究专题通过 `ResearchPage.astro` 挂载 `ResearchRoute client:load`。React 路由组件再根据 route 动态加载完整研究页面，因此静态正文仍在 React 中生成。

说明文档继续由 MkDocs 构建到 `/docs/`。本次不迁移 MkDocs，不改变公开 URL，不改变研究数据文件和 Python 计算流程。

## 目标边界

- 页面路由由 `web/src/pages/` 和 Astro 文件路径决定。
- 页面标题、研究问题、结论、数据范围、方法、限制和静态表格由 Astro 输出。
- 图表、时间窗口、筛选、搜索和排序表格保留为 React Islands。
- 公开数据继续使用 `web/public/data/` 中的生成快照。
- 研究计算继续在 Python 和既有研究代码中完成。
- 首阶段删除 `ResearchRoutes.tsx`，不要求首阶段完成所有静态正文拆分。
- React Islands 按需使用 `client:load`、`client:visible` 或 `client:idle`。

## 迁移顺序

1. 解除 Astro 页面与 React 二次路由的耦合。每个专题 Astro 页面直接挂载对应 React 组件，并删除 `ResearchRoutes.tsx`。
2. 将现有 React 研究页面拆为 Astro 静态正文和小型 React Islands。先处理风格因子、微盘和现金流，再处理流动性。
3. 将大组件中的图表、交互表格和筛选器拆出到 `web/src/components/islands/`，静态内容移到 `web/src/components/research/` 或对应 Astro 页面。
4. 整理 CSS 文件边界，不改变现有视觉设计和深色模式。
5. 运行页面构建、Node 测试和静态产物检查，确认 URL、数据快照和文档入口不变。

## 验收标准

- `ResearchRoutes.tsx` 不再被任何 Astro 文件引用，并被删除。
- 研究专题可以直接从各自 Astro 页面看到标题、研究摘要和静态说明。
- 页面只在真正需要交互的位置加载 React。
- `npm run build` 通过，Astro check 为 0 errors、0 warnings、0 hints。
- 既有 Node 测试通过，静态产物仍包含 `docs/`、数据 manifest 和研究页面。
- `git diff --check` 通过。

