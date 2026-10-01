# 数据保存与公开发布

> English canonical: [Data storage and publication](data-storage-and-publication.en.md).

本仓库保存研究代码和经过审核的派生结果。原始行情由 `quant-market-data-platform` 管理，完整研究运行结果写入仓库外的稳定目录。

## 数据分层

| 层级 | 内容 | 常用格式 | 保存位置 |
|---|---|---|---|
| 原始数据 | 逐股票逐日行情、估值、复权和状态字段 | Parquet | `quant-market-data-platform` |
| 研究中间结果 | 大型面板、逐股票逐日结果和重复计算缓存 | Parquet、DuckDB | 仓库外输出目录 |
| 公开派生结果 | 年度汇总、分位数、降采样曲线和已审查指标 | CSV、JSON | `web/public/data` |
| 研究说明 | 计算口径、来源、覆盖范围和限制 | Markdown、JSON | Git 仓库 |

不要将供应商原始数据、凭证、完整行情面板或本机路径提交到仓库。

## 文件格式

CSV 适合体量较小、需要人工核对的公开结果。它便于查看差异，也能直接供浏览器读取。Parquet 适合较大的分析数据，字段类型明确、压缩率高，也方便 DuckDB 按列和条件读取。

大型结果采用 `Parquet + manifest + 小型摘要 CSV/JSON`。浏览器若需读取 Parquet，可以使用 DuckDB-WASM 或 Apache Arrow，仓库仍保留可审查的摘要文件。

## 体量参考

以下数值用于日常维护，具体发布方式按研究需要决定：

- 小于约 10 MB 的派生文件通常可用 CSV。
- 约 10 至 50 MB 的文件可考虑压缩、拆分、降采样或只发布摘要。
- 超过约 50 至 100 MB 的文件应放到仓库外的 Parquet 或对象存储。
- 公开派生数据合计接近 50 MB 时，重新检查页面发布范围。
- 原始逐股票逐日数据始终保存在外部数据平台。

当前公开派生数据只有几 MB。新增研究应优先覆盖稳定文件名，避免持续增加带日期的重复副本。

## Manifest 内容

大型或重要的研究输出至少记录：

- 数据结构版本。
- 生成时间。
- 数据来源和覆盖范围。
- 行数与关键筛选条件。
- 文件格式、大小和校验和。
- 文件属于原始数据还是已审核的派生结果。

微盘成交额报告包含：

- `smallcap_turnover_daily.csv`：完整的每日分组汇总，保存在仓库外。
- `smallcap_turnover_summary.json`：覆盖范围和研究限制。
- `smallcap_turnover_manifest.json`：数据结构、文件大小、行数和 SHA-256。

2008 年起的扩展版本使用不同历史数据源，并在 summary 和 manifest 中标记 `quality_status = incomplete`。历史源缺少可靠的 ST 和停牌字段，因此这段序列适合长期描述，不能与 2015 年后的清洗版本合并成同一质量等级。

A 股清洗面板只有在 `manifest.yml` 声明 `tushare.a_share.daily_clean.v2`、记录 `inputs.st_history_file` 和 `market-data-platform.reconstructed-st-history.v2` receipt，并声明 `daily_clean.st_available_from.v1` 契约时，才可将 ST 来源标记为已验证。保留持仓报价的面板为 `derived`。旧版或缺少 `st_available_from` 的数据标记为 `incomplete`，ST 资格视为未知，不得用于新建仓。对 `is_st=true` 的行，只有 `st_available_from` 不晚于决策日时才可确认当日状态；日期缺失或晚于决策日时资格仍未知。保留持仓报价的模式仍可检查真实价格。该历史 ST 表按生效日期重建，receipt 中的 `revision_safe=false` 表示历史修订可得性仍未完全得到证明。

页面只展示审核后的摘要或降采样结果，不读取完整逐股票逐日面板。当前小微盘成交额页面读取 `web/public/data/smallcap_turnover.json`，内容包括年度和月度汇总、覆盖质量、N=1 极端诊断、股票数量选项和重叠审计摘要。完整的清洗日频结果、历史日频结果和审计明细保存在仓库外。

口径审计结果也保存在仓库外。Git 只保存可重跑命令、测试和方法文档，不存放大体量审计 CSV。
