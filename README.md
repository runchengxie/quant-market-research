# quant-market-research

这里记录可复算、可浏览的市场研究，主题包括跨市场股票、流动性、容量和指数复现。

共享数据由 `quant-market-data-platform` 管理，通用回测和执行模拟由
`quant-platform` 提供。私有信号、模型和飞书选股研究保留在 `quant-research`。
本项目是独立仓库，Python 包名 `market_research` 和命令 `market-research` 沿用现有名称。
原始数据、缓存和完整运行结果保留在仓库外，不复制数据副本。本仓库当前没有 Git 子模块。

## 现金流与微盘研究笔记

```bash
uv run market-research report index-study --study studies/index_replication/study.example.json
```

示例只读共享行情，结果写在仓库外。换一台机器运行前，应先修改示例配置中的路径。
报告会生成覆盖率、指数比较、标准化净值和运行收据，并输出本地 HTML 页面。
报告还包括回本水下期、买入后等待时间、固定持有期亏损比例及对应的 HTML 页面。
长窗口配置见 `studies/index_replication/recovery.study.json`，计算口径见
`studies/index_replication/recovery-methodology.md`。
主网页首页展示研究摘要，回本数据和计算方法收录在现金流与微盘专题中。
两个专题还展示经过复核的指数复刻汇总，分别比较价格回报和税前全收益。
数据来源、固定实验区间和待补证据见 [复刻研究记录](studies/index_replication/replication-progress-20260909.md)。
旧网页 `research/recovery.html` 会跳转到 `#cashflow-recovery`，不要用本地报告覆盖跳转页。
现金流按价格指数统一比较沪深 800、国证 2000、中证 A500、中证 1000、中证全指和中证 500。
微盘研究纳入同花顺、万得及中证 2000、国证 2000 对照。数据缺口会明确标记，不用代理序列补齐。
这是行情证据层，不能把它当作已完成成分复刻。研究进度和阻断项见
`studies/index_replication/README.md`。

迁移后旧路径保留兼容链接和已有 worktree，以免影响其他在途任务。详见 `docs/quant-family-migration.md`。

本项目承接 `index-research` 和 `market-liquidity-profiles` 的持续维护与独立发布工作。旧仓库保留历史代码和研究记录。当前维护的代码、公开页面和派生快照集中在本仓库，旧仓库作为历史档案保留。

项目采用本地优先的方式读取现有行情资产，不把原始数据复制到仓库。当前支持 A 股、港股、美股和日股。

## 本地环境

```bash
uv sync --extra dev --extra duckdb
cp configs/local.example.toml configs/local.toml
uv run market-research --help
uv run market-research config inspect --output-root outputs
```

本地配置包含机器相关路径，已被 Git 忽略。请不要在配置文件中填写凭证。

数据目录由 `configs/local.toml` 中的 `sources` 配置。请按本机实际位置填写 `a_share_root`、港股数据路径、美股数据路径和 `jp_root`。配置模板中的路径仅作示例，仓库不保存本机目录位置。

日股适配器目前只读取 `daily/*/equities_bars_daily_*.parquet`，并将 J-Quants 的 `Date`、`Code`、`C`、`Vo` 和 `Va` 映射到统一面板。当前 nira 快照没有配套的日频市值字段，因此日股的市值相关分析会标记为 `incomplete`，直到补充相应数据。

## 测试与构建

本地验证命令与 GitHub Actions 使用同一套入口。Python 测试覆盖命令行、市场数据适配器、计算结果和报告输出；Ruff 检查 Python 代码；MkDocs 检查公开说明站；网页测试和构建检查前端。

```bash
uv run --extra duckdb --with pytest pytest -q
uv run --extra dev ruff check src tests
uv run --extra docs mkdocs build --strict

cd web
npm ci
npm test
npm run build
```

`mkdocs build` 只生成 `web/dist/docs/`，网页构建只处理主站。GitHub Actions 会在拉取请求中运行这些测试和构建，并检查公开产物中是否包含本机路径或凭证标记。部署只会在推送到 `main` 后执行。

架构和迁移范围见 `docs/superpowers/specs/2026-09-07-market-research-design.md`。首个报告包包括流动性汇总、覆盖率诊断、基于滞后流动性特征的机械容量面板，以及来源元数据。
数据保存、Parquet/CSV 分工和公开发布边界见 `docs/data-storage-and-publication.md`。

## 迁移后的命令

```bash
uv run market-research report microcap --config configs/local.toml
uv run market-research report indices --config configs/local.toml
uv run market-research report etf-pairs --config configs/local.toml
uv run market-research report cashflow --config configs/local.toml
uv run market-research report liquidity --config configs/local.toml
uv run market-research report smallcap-turnover --config configs/local.toml
uv run market-research report smallcap-turnover-history --config configs/local.toml
uv run market-research report smallcap-turnover-audit --config configs/local.toml
uv run market-research report barra-risk-inputs --config configs/local.toml
uv run market-research validate --config configs/local.toml
```

`microcap` 还会生成旧项目公开快照所需的年度收益、滚动 CAGR、滚动回撤和来源标记文件。`indices` 覆盖指数价格回报和 ETF 复权代理，`etf-pairs` 覆盖指数与 ETF 配对、比较和流动性代表，`cashflow` 覆盖现金流指数研究。输出文件沿用旧项目的命名，生成入口统一为本项目。

其他研究报告和数据刷新入口：

```bash
uv run market-research report index-study --study studies/index_replication/study.example.json
uv run market-research report style-factors --study /path/to/local-style-study.yml
uv run market-research report global-six-market --study studies/global_six_market/study.yml
uv run market-research fetch linked-indices --config configs/local.toml
uv run market-research fetch cashflow --config configs/local.toml
```

`index-study` 生成指数比较与回本风险报告。`style-factors` 生成风格因子分组结果。`global-six-market` 运行六市场 ETF 代理组合研究，该研究仍处于探索阶段。`fetch` 会在配置的输出目录中更新指数或现金流数据。

研究命令需要外部行情路径。六市场配置中的 `data_root` 是占位值，运行前必须修改。`studies/style_factors_18y/study.yml` 记录研究范围，不含必需的本机 `panel_path`，需另建本地配置后再运行。

## Barra / 风格因子研究

`market-research` 是 Barra 和风格因子市场证据的统一入口。`[barra].result_root` 可读取 quant 中的历史结果作为来源记录，原始行情和实验缓存仍保留在 quant 数据目录。

```bash
uv run market-research report barra --config configs/local.toml
```

该命令输出历史 19 个因子摘要，以及基于标准 A 股面板重新计算的市值分位收益和尾部排序诊断。页面将结果标记为历史描述性证据。日频横截面观测存在时间相关性，不能直接视为独立样本，也不能据此认定统计显著或策略有效。

研究页面区分历史档案、进行中的专题和待补数据。现金流、小微盘、指数与 ETF、Barra 和 18 年因子研究属于历史档案。跨市场小微盘流动性仍在研究中，六市场比较和日股同口径分桶仍待补数据。完整范围见 `docs/research-information-architecture.md`。

18 年风格研究和六市场 ETF 代理配置研究位于 `studies/`。alpha、signal、IC、decay
和策略决策属于 `quant-research`，通用回测与执行模拟属于 `quant-platform`。
六市场研究仍处于探索阶段，不提交订单，也不把 ETF 代理结果当作完整的国家股票市场表现。

## GitHub Pages

公开页面只使用派生文件，不发布原始行情、机器路径和凭证。运行本地页面：

```bash
cd web
npm ci
npm run snapshot  # 仅在刷新本地派生快照时运行
npm run dev
```

经审查的因子定义、研究解释和限制说明由 MkDocs 发布在同一 Pages 站点的
[`/docs/`](https://runchengxie.github.io/quant-market-research/docs/)。本地可运行
`uv run --extra docs mkdocs serve` 预览。说明站只发布首页和两篇经过审查的因子研究文档，不会公开其余内部文档。

推送到 `main` 后，GitHub Actions 会运行 Python 测试、网页测试和构建，再发布主网页与说明站。页面地址为：

<https://runchengxie.github.io/quant-market-research/>
