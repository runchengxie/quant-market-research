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
| Barra 历史摘要和市值分组 | `report barra` | 历史摘要及市值分组诊断 |
| Barra 风险模型输入 | `report barra-risk-inputs` | 风险输入文件和覆盖诊断 |
| 18 年风格因子分组 | `report style-factors` | 因子分组收益和摘要 |
| 六市场 ETF 代理组合 | `report global-six-market` | 按研究配置生成的结果，状态仍为探索 |
| 指数与回本风险研究 | `report index-study` | 指数比较、回本等待和持有期风险 |

行情下载由 `fetch linked-indices` 和 `fetch cashflow` 执行。数据只写入配置的输出目录，不将供应商原始行情复制到 Git。

## 已知差异

1. 统一数据面板保留各市场本币。跨市场换算在后续计算中完成，并在元数据记录 `currency` 和 `fx_method`。
2. 日股适配器目前没有配套市值来源。报告会将日股市值相关结果标记为 `incomplete`。
3. 微盘重建按总市值选取最小 400 只股票，并在下一交易日执行。这是一项研究规则，不代表 Wind 指数复刻或真实账户收益。
4. 报告命令生成 JSON 和 CSV 派生数据，网页读取经过筛选的公开文件。MkDocs 说明站仅发布 `docs/index.md`、低换手和微盘研究两页，内部 runbook 不公开。

`quant-research` 负责 alpha 假设、信号验证、IC 与衰减分析、策略实验和组合决策。`quant-platform` 负责通用回测、组合、风险、成本、执行模拟和产物契约。本仓库不复制原始行情或私有实验缓存。
