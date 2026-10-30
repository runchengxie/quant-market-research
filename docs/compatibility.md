# 历史兼容与职责边界

`quant-market-research` 是市场研究代码和公开研究页面的维护入口。旧项目 `index-research`、`market-liquidity-profiles` 和 `nira` 保留各自的历史代码、数据和研究记录，本仓库不再依赖它们发布页面。本仓库没有 Git 子模块。

迁移期间使用小型确定性样本和旧项目纯函数测试检查结果。完整历史数据对账仍需访问对应的本地快照。对账完成前，旧项目可用于核对历史结果，但不承担新的发布工作。

## 当前报告入口

| 研究能力 | 命令 | 主要输出 |
|---|---|---|
| 微盘规则重建与快照 | `report microcap` | `microcap/` 和旧格式兼容文件 |
| 指数价格收益与 ETF 研究 | `report indices` | `a_share_index_price_returns.csv` |
| ETF 与指数配对、排序 | `report etf-pairs` | `linked_indices/` |
| 现金流指数快照 | `report cashflow` | `cashflow_indices/` |
| 跨市场流动性分组 | `report liquidity` | `liquidity_summary.csv`、`liquidity_report.json` |
| 理论容量诊断 | `report liquidity` | `capacity_surface.csv` |
| 市场风格历史摘要和市值分组 | `report barra` | 历史摘要及市值分组诊断 |
| 风格风险模型输入 | `report barra-risk-inputs` | 风险输入文件和覆盖诊断 |
| 18 年风格因子分组 | `report style-factors` | 因子分组收益和摘要 |
| 六市场 ETF 代理组合 | `report global-six-market` | 按研究配置生成的结果，状态仍为探索 |
| 指数与回本风险研究 | `report index-study` | 指数比较、回本等待和持有期风险 |

行情下载由 `fetch linked-indices` 和 `fetch cashflow` 执行。数据只写入配置的输出目录，不将供应商原始行情复制到 Git。

## 已知差异

1. 统一数据面板保留各市场本币。跨市场换算在后续计算中完成，并在元数据记录 `currency` 和 `fx_method`。
2. 日股适配器目前没有配套市值来源。报告会将日股市值相关结果标记为 `incomplete`。
3. 微盘重建按总市值选取最小 400 只股票，并在下一交易日执行。这是一项研究规则，不代表 Wind 指数复刻或真实账户收益。
4. 报告命令生成 JSON 和 CSV 派生数据，网页读取经过筛选的公开文件。Astro 说明页只渲染 `web/src/content/public-registry.ts` 明确登记的文档，内部 runbook 不公开。

`quant-research` 负责 alpha 假设、信号验证、IC 与衰减分析、策略实验和组合决策。`quant-platform` 负责通用回测、组合、风险、成本、执行模拟和产物契约。本仓库不复制原始行情或私有实验缓存。

## Market Style Analysis naming and reader contract

The current public name is **市场风格分析 / Market Style Analysis**. The long-history page uses **18 年 A 股市场风格分析**. New Python callers use `market_research.style_factors.load_style_factor_summary` and `summarize_style_factor_file`; `market_research.barra` remains a compatibility import. New commands are `report style-factors` and `report style-risk-inputs`; the former `barra` / `barra-risk-inputs` commands and `[barra]` / `[barra_risk]` configuration remain accepted. Prefer `[style_factors]` / `[style_risk]` in new configuration. Output filenames, persisted keys, snapshot IDs, CSS/anchor selectors, old documentation URLs and immutable `data/barra` sources retain their historical names for existing consumers. Archived plans, source records and exact commercial-model references retain their original wording.

`/data/style-factors/reader.json` is a static, build-time projection of the reviewed `historical_factor_summary.json` and `factor_yearly.csv` archive. Under GitHub Pages prepend the site base `/quant-market-research`. Schema version 1 has `evidenceStage: historical_archive`, `unit: percent`, row-derived coverage, SHA-256 hashes of the exact summary/yearly bytes, and all 19 original factor IDs in summary order. Annual observations are sorted by year, use **period_return**, retain actual period dates, days and partial flags, and omit missing years. Values are percent units (4.54 means 4.54%), without annualization, zero filling or direction reversal. Invalid rows, duplicate factor/year observations and dates outside their row year fail the build.

The archived report describes **high-score minus low-score** portfolios, not uniformly high raw descriptors minus low raw descriptors: value uses inverse PB, low volatility/low leverage/low beta have their own favorable-score directions. Its factor table records large-minus-small for historical size. The original descriptor-to-series chain remains incompletely verified. The current descriptor dictionary mixes `high_minus_low` and `low_minus_high` and is a separately inspected definition, not proof of the archive's original formulas. The independently recomputed size diagnostic uses **small-minus-large**, the opposite of archived size. The reader preserves archived signs and does not claim standardized commercial-model returns or actual account returns.
