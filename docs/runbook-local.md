# 本地运行手册

## 安装

```bash
uv sync --locked --extra dev --extra duckdb
cp configs/local.example.toml configs/local.toml
```

编辑 `configs/local.toml`，让每个数据源指向本机已有的数据目录。该文件已被 Git 忽略，因为其中包含机器相关路径。处理大型 A 股 Parquet 目录时，将 `use_duckdb = true`，并通过 `uv sync --extra duckdb` 安装 DuckDB 依赖。

## 检查数据目录

```bash
uv run market-research validate --config configs/local.toml
```

该命令只检查配置的数据目录是否存在，不会读取全部行情数据。

## 构建流动性报告

```bash
uv run market-research report liquidity --config configs/local.toml
```

结果会写入 `output_root`：

- `liquidity_report.json`
- `liquidity_summary.csv`
- `coverage_diagnostics.csv`

## 构建 A 股微盘重建

```bash
uv run market-research report microcap --config configs/local.toml
```

该结果使用最小市值 400 只股票等权的研究规则，不代表 Wind 官方 `8841431.WI` 指数。计算中没有模拟交易成本、涨跌停成交、停牌成交、市场冲击和策略容量。

## 构建最小市值股票成交额统计

```bash
uv run market-research report smallcap-turnover --config configs/local.toml
```

该报告按每日总市值选取最小的 1、10、50、100、200、400 和 1000 只 A 股，统计成交额
总和、均值、中位数和分位数。N=1 只作为极端诊断，不代表可交易组合。完整的 `smallcap_turnover_daily.csv`、摘要和 manifest
写入配置的仓库外 `output_root`，不会自动进入 Git 或公开页面。

如果需要 2008 年起的扩展版本：

```bash
uv run market-research report smallcap-turnover-history --config configs/local.toml
```

该版本连接 2008 年起的 daily 与 daily_basic，覆盖尽可能长的历史，但由于历史源没有
可靠的 ST 和停牌字段，输出会标记为 `incomplete`，不能与 2015 年后的清洗版本直接混为
同一质量等级。

如果需要把微盘最大回撤和水下时间向前延长，可运行：

```bash
uv run --locked --extra duckdb python scripts/analyze_microcap_history.py \
  --data-root /path/to/quant-market-data-platform \
  --output /path/to/research-outputs/microcap-history
```

该脚本组合 2008–2014 年历史行情与 2015 年后的清洗日频面板，构造最小 50、100、200、400、800
只股票的等权序列，并输出停牌估值和无法分类缺价的敏感性分析。输入目录需指向 `quant-market-data-platform` 数据根目录。`--output` 必填，应指向仓库外的研究结果目录。
信号在形成日收盘后生成，下一交易日收盘成交，再从执行日收盘计算持有收益。该规则重建不代表 Wind 官方序列，也没有计入成本、涨跌停成交限制或容量模型。研究结论见
`docs/research/experiments/turnover-microcap-followup-20260915.md`。

生成两套口径的重叠期审计：

```bash
uv run market-research report smallcap-turnover-audit --config configs/local.toml
```

该命令比较共同日期和 N 分组下的成交额中位数差异，并输出 5%、10% 和 25% 误差范围
覆盖比例。它用于发现口径变化，不把历史源提升为已验证数据。

网页发布年度和月度汇总。月度值先计算每个交易日的成交额中位数，再取月度中位数。可以用以下
命令从仓库外日频结果刷新网页快照：

MARKET_RESEARCH_OUTPUT_ROOT=/path/to/research-outputs node web/scripts/build-smallcap-turnover-public.mjs

## 日股股数估算辅助脚本

`scripts/build_yfinance_shares_sidecar.py` 根据 NIRA 中的日股行情，从 Yahoo Finance 获取上市股数估算。该结果只用于本地探索，不能替代授权来源。先安装可选依赖，再指定数据根目录和输出文件：

```bash
uv sync --locked --extra yahoo
uv run --locked --extra yahoo python scripts/build_yfinance_shares_sidecar.py \
  --jp-root /path/to/japan-market-data \
  --output /path/to/local-output/shares-sidecar.parquet \
  --start 2020-01-01
```

脚本支持按代码筛选、设置请求间隔和并发数，也支持保存检查点与失败记录。Yahoo Finance 数据的覆盖和质量不作完整性保证。运行结果保存在本机，不会自动发布。

## 数据目录配置

数据位置填写在 `configs/local.toml` 的 `[sources]` 下。A 股使用 `a_share_root`，港股使用 `hk_daily_root`、`hk_valuation_root` 和 `hk_instruments_path`，美股使用 `us_shareprices_path`，日股使用 `jp_root`。先从 `configs/local.example.toml` 复制模板，再替换为本机已有目录。

## 其他报告和数据刷新

完整报告清单、输入和主要输出见[职责与报告说明](compatibility.md)。常用命令如下：

```bash
uv run market-research report indices --config configs/local.toml
uv run market-research report etf-pairs --config configs/local.toml
uv run market-research report cashflow --config configs/local.toml
uv run market-research report smallcap-turnover-audit --config configs/local.toml
uv run market-research report barra-risk-inputs --config configs/local.toml
uv run market-research report index-study --study studies/index_replication/study.example.json
uv run market-research report style-factors --study /path/to/local-style-study.yml
uv run market-research report global-six-market --study studies/global_six_market/study.yml
uv run market-research fetch linked-indices --config configs/local.toml
uv run market-research fetch cashflow --config configs/local.toml
```

示例研究配置中的数据路径需要按本机目录调整。风格因子研究还需提供本地面板路径。六市场 ETF 代理组合处于探索阶段，不代表六个国家的完整股票市场表现。

## 本地网页和公开快照

首次安装网页依赖并启动开发服务器：

```bash
cd web
npm ci
npm run dev
```

网页读取仓库内经过筛选的派生快照。需刷新微盘摘要时运行 `npm run snapshot`，该命令从默认 `outputs/` 读取本地研究结果。成交额网页使用独立生成脚本：

```bash
MARKET_RESEARCH_OUTPUT_ROOT=/path/to/research-outputs \
  node web/scripts/build-smallcap-turnover-public.mjs
```

更新代码后可在 `web/` 目录运行 `npm test` 和 `npm run build`。Python、Ruff 和 MkDocs 检查命令见仓库根目录 `AGENTS.md`。GitHub Pages 工作流会先构建首页，再生成 MkDocs 说明站，公开输出位于 `web/dist/`。`scripts/sync_public_research_data.py` 依赖旧 `index-research` 仓库的本地产物，仅供迁移期间使用，不属于当前发布流程。

## Barra / 风格因子报告

在 `configs/local.toml` 中配置 A 股数据根目录和可选的历史风格因子结果目录后运行：

```bash
uv run market-research report barra --config configs/local.toml
```

输出包括：

- `barra_summary.json`：历史因子摘要、数据来源和市值单调性指标。
- `barra_size_quantiles.csv`：按形成日和市值升序分位的未来收益。
- `barra_source_manifest.json`：canonical 项目、历史结果和原始数据的 provenance。

市值分位中 Q1 是最小市值组。`monotonicity_score` 表示相邻分位中小市值组收益不低于大市值组的比例，不能代替显著性检验。解读时还需考虑成本、容量、停牌和幸存者偏差。
