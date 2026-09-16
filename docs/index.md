# Quant Market Research 研究说明

这里介绍公开网页所展示的研究问题、计算口径和证据限制。主网页便于查看图表，说明站记录研究方法、结果含义和仍需补充的验证。说明站只发布经过审核的页面，其他内部文档不会进入公开站点。

专题网页采用报告式结构，先给出结论，再放关键数字、证据边界和下一步。低换手页面是这套图文混合模板的首个版本，完整的定义和复现说明仍在本说明站中维护。

## 因子研究

- [低换手：它可能反映哪些特征](research/factors/low-turnover.md)：介绍代理变量、逐步归因、组内排序、可交易性和下一轮检验。
- [微盘股：收益证据与水下时间](research/factors/microcap.md)：介绍最小市值组合的回撤、长期未创新高、早年数据限制和审计路线。

## 网页和说明站如何共存

项目使用 Astro 生成静态多页研究网站，图表和筛选等交互由 React 与 ECharts 提供。MkDocs 继续生成研究说明站。两者位于同一 GitHub Pages 站点：Astro 先输出到 `web/dist/`，MkDocs 再将选定的公开文档写入 `web/dist/docs/`。主页和说明站共用 `docs/assets/theme-tokens.css` 中的颜色与字体变量。发布流程不会公开仓库里的所有内部文档。

本地预览说明站：

```bash
uv run --locked --extra docs mkdocs serve
```

本地构建会生成 `web/dist/docs/`。完整发布还会构建 Astro 网页、检查静态文件与公开数据边界，并运行浏览器冒烟测试。配置和发布流程见仓库根目录的 `web/astro.config.mjs`、`mkdocs.yml` 与 `.github/workflows/pages.yml`。

仓库内 `docs/superpowers/` 保存设计稿和实施计划，记录编写时的方案与待办状态。判断当前功能时，以本索引和对应专题文档为准。
