# Quant Market Research 研究说明

这里整理公开网页背后的研究问题、计算口径和证据边界。网页负责快速浏览图表；这份说明站负责完整解释研究怎么做、结果能说明什么，以及还缺什么验证。

## 因子研究

- [低换手：它可能在替哪些东西“说话”？](research/factors/low-turnover.md)：解释代理变量、逐步归因、组内排序、可交易性和下一轮检验。
- [微盘股：收益证据与“水下多久”](research/factors/microcap.md)：解释最小市值组合的回撤、长时间未创新高、早年数据限制和审计路线。

## 网页和说明站如何共存

项目保留 React/Vite 研究网页作为首页，MkDocs 说明站发布在同一 GitHub Pages 站点的 `/docs/` 子路径。两者是同一仓库、同一次 Pages 发布：Vite 生成 `web/dist/` 根站，MkDocs 只把经审查的公开文档生成到 `web/dist/docs/`。发布流程不会把仓库里的全部内部文档公开。

本地预览说明站：

```bash
uv run --extra docs mkdocs serve
```

本地构建会生成 `web/dist/docs/`；完整发布还会先构建主网页。配置和发布工作流见仓库根目录的 `mkdocs.yml` 与 `.github/workflows/pages.yml`。
