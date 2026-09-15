# Barra 研究迁移记录

## 项目职责

`market-research` 现在是跨市场 Barra 和风格因子研究的统一入口。`quant` 继续管理行情资产、回测运行、notebook 和历史实验结果。

## 接入的历史数据

本次接入的历史结果目录为：

`<共享数据根>/strategy_outputs/style-factors/weekly-20260904`

该结果包包含 19 个因子：beta、chip concentration、dividend yield、earnings yield、fund breadth/ownership、growth、institution holding、leverage、liquidity、liquidity flow、lowvol、momentum、ps value、quality、size 和 value。

## 当前分析能力

`market-research report barra` 读取历史清单、元数据和因子摘要，并对统一 A 股面板执行市值因子分位分析。Q1 表示最小市值组。报告输出未来持有期收益、尾部价差、分位排序诊断和覆盖信息。该结果属于历史描述性证据，形成日之间存在时间相关性，不能直接视为独立样本或统计显著性检验。

## 口径限制

原历史报告使用月末五分位大市值组减小市值组的多空口径，没有保存纯市值十分位或二十分位曲线。因此历史摘要只作来源记录，分位排序诊断以新命令生成的 `barra_size_quantiles.csv` 为准。正式显著性结论仍需另行设计统计检验。

## 网页收益口径（2026-09-09 核对）

核对历史包 `style-factors/weekly-20260904` 的 `meta.json`、
`style_analysis_report.md`，以及生成端 `style_factors/workflow.py` 和
`portfolio_backtester/style_factors_backtest.py` 后，网页按以下口径标注：

- 每月末按因子得分分五组，两端初始等权并固定份额持有。日序列为最高分组收益减最低分组收益，市值因子方向为大市值减小市值。
- 总览的 `geometric_annual_ret` 按 `product(1 + daily_spread) ** (252 / observations) - 1` 计算。逐年 `annual_ret` 按当年 `product(1 + daily_spread) - 1` 计算，不将单年收益外推成年化值。源文件以百分数记录，网页除以 100 后再格式化为百分比。
- 年化、年度收益、波动、Sharpe、回撤和胜率均描述历史多空合成序列。相关性也按多空日收益差计算。这些数值尚未验证能否在策略账户中实现。
- 历史计算将持仓期缺失收益记为零，退市终值及完整执行限制未验证。逐期券源、借券成本、保证金和资金占用尚未验证，不能由本页判断具体 A 股组合可执行或一概不可执行。
- 风格风险分析可用于解释暴露和收益来源。部分 Barra 分析用于风险解释，并不预测未来收益。IC、Rank IC 和分位单调性可以检查因子得分与未来收益的关系，仍需统计检验和样本外验证。本页没有发布 IC 或 Rank IC 数值。
- 历史数据包使用原始日行情、日频估值和后续重建的财务数据。按公告日对齐及部分持仓点时处理，无法证明所有历史财务版本都满足完整点时要求。行业信号去均值也不能保证组合行业权重中性。

公开依据为 [历史摘要](../web/public/data/barra/historical_factor_summary.json)、
[年度派生表](../web/public/data/barra/factor_yearly.csv)、
[相关性](../web/public/data/barra/factor_correlation.json) 和
[来源清单](../web/public/data/barra/barra_source_manifest.json)。本次只改展示文字，
不重算或更换派生数据，不复制生成端代码、原始数据或私有研究内容。

回本研究现已并入现金流和小微盘专题。总览只保留简短发现、数据日期、研究进度和专题入口。
旧 `./research/recovery.html` 地址跳转到主站 `#cashflow-recovery`，详细统计和计算方法在专题内阅读。

验证时运行 `cd web && npm test && npm run build`，并按 Pages 工作流扫描
`web/dist` 中的本地路径和凭证标记。还需确认 `git diff -- web/public/data` 为空。
浏览器验收应检查总览入口的可见性和相对地址、Barra 多空合成标签与研究边界、
因子切换后年化值与公开摘要一致，以及市值十分位仍保持独立诊断口径。

本次验证结果：Python 59 项、前端 12 项通过，生产构建成功。构建仍显示既有的 ECharts
分块超过 500 kB 提示。公开边界扫描、`git diff --check` 和公开数据零差异检查均通过。
公开摘要、年度表和相关性文件经 `cmp` 与历史包对应文件逐字节一致。
Chromium 实际渲染检查通过：总览链接可见且地址准确，Barra 口径与限制说明可见，
19 个因子逐一切换后的年化值与公开摘要一致，移动端年度标题可见且无页面异常。
本次没有新增功能 helper 或源码字符串断言测试。研究摘要 HTML 内容和链接的验收已由回本研究任务完成。需要检查真实 HTML 页面，Vite 的单页回退响应无法代替这项验收。
