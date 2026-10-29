# 海外半导体历史数据：开盘缺口有关联，ETF 尚无稳健改善

[10月29日较早的目录检查](overseas-theme-20261029.zh-CN.md)记录了当时缺少主题输入。随后完成了限定范围的 Yahoo 取数、日线一致性检查，并实际运行了三组现有主题实验。较明显的结果集中在申万半导体开盘缺口；额外延迟一个 A 股观测日后消失。开盘后收益与 512480 下一交易日开盘收益的合并样本 MSE 改善区间均跨零。结果属于回顾性探索，不是今日信号，也没有晋升模型。[English](overseas-theme-source-results-20261029.md)

## 数据范围与口径

| Symbol | Rows | First / last session | Missing / extra / duplicate | Price / OHLC errors |
| --- | --- | --- | --- | --- |
| ^SOX | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| SMH | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| SOXX | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| NVDA | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| AMD | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |
| AVGO | 2721 | 2016-01-04 / 2026-10-28 | 0 / 0 / 0 | 0 / 0 |

请求区间为 2016-01-01（含）至 2026-10-29（不含），排除了10月29日美国日线。六个标的均完整覆盖 2,721 个 XNYS 交易日，无缺日、多余日期或重复日期；有限正价格、OHLC 上下界及非负成交量检查通过。保留了带纽约时区的日期、分红拆股字段，以及含节假日、夏令时和提前收盘的交易日历。这是内部一致性检查，未独立核对供应商价格。六次供应商调用均首次成功；取数前的本地日历起始日错误已改为1月4日，没有造成失败供应商请求。

版本、UTC 起止时刻及完整参数见英文记录和外部 `source_receipt.json`。关键参数为 `auto_adjust=False, actions=True, repair=False, keepna=True`，日频区间和超时显式指定；失败最多重试三次，间隔2/4秒，实际未触发供应商重试。

`auto_adjust=False` 返回的 Yahoo OHLC 仍已处理历史拆股，不能称为当时未复权的名义价格；`Adj Close` 还包含供应商的现金分配调整，只作为总回报代理，未经独立再投资重建认证。SOX 使用指数点数 `Close`；SMH/SOXX 使用美元每份的 `Adj Close`。NVDA、AMD、AVGO 已获取并检查，但没有加入这三组主题实验，也没有重建历史指数成分。

## 实际运行结果

生成结果的代码提交为 `5122f1abd54bc69037631a4d45f8e28c24a29647`，现有 runner 在运行和导出时均检查工作区干净及版本一致。实验总体预测区间为 **2020-01-02 至 2026-10-16**，由已有国内与控制变量输入截断；海外新数据到10月28日不代表实验延伸到该日。ETF 满足至少252行训练要求后，测试折从2021年开始。保留了已知的 512480 在2021-03-26停牌及排除交叉汇率报价的既有审计处理。

基准 `global` 包含国内滞后收益、动量、波动率、沪深300、汇率及标普500；增强模型为 `theme_residual`。每年扩展训练只用训练行估计截距与标普 beta，并清除首个测试决策前尚未结束的训练标签。标普已在基准内，残差化只是线性重新参数化，不证明因果。延迟0使用假设已到达的最近完整美股收盘；延迟1把已对齐输入延后一个 A 股观测日。上海时间08:45决策、美股常规收盘后再等一小时及夏令时处理，属于可用性假设，没有历史实际到达记录。

以下正值表示增强模型相对基准降低 MSE，单位为基准 MSE 的百分比，不是收益百分点。95%区间来自十个观测一块的配对重采样，仅作描述，未做多重检验校正。

| Theme | Target / outcome | Delay | n | MSE gain % | Descriptive 95% interval % |
| --- | --- | --- | --- | --- | --- |
| SOX | sw_semiconductor / gap | 0 | 1643 | 5.800 | [3.405, 8.945] |
| SOX | sw_semiconductor / post_open | 0 | 1643 | 0.103 | [-0.317, 0.455] |
| SOX | sw_semiconductor / gap | 1 | 1634 | -0.165 | [-0.485, 0.125] |
| SOX | sw_semiconductor / post_open | 1 | 1634 | -0.020 | [-0.454, 0.395] |
| SOX | 512480 / next_tradable_open | 0 | 1398 | -0.104 | [-0.762, 0.544] |
| SOX | 512480 / next_tradable_open | 1 | 1390 | -0.582 | [-1.421, 0.235] |
| SMH | sw_semiconductor / gap | 0 | 1643 | 5.600 | [3.400, 8.461] |
| SMH | sw_semiconductor / post_open | 0 | 1643 | 0.044 | [-0.278, 0.344] |
| SMH | sw_semiconductor / gap | 1 | 1634 | -0.202 | [-0.558, 0.143] |
| SMH | sw_semiconductor / post_open | 1 | 1634 | -0.072 | [-0.564, 0.392] |
| SMH | 512480 / next_tradable_open | 0 | 1398 | -0.083 | [-0.748, 0.537] |
| SMH | 512480 / next_tradable_open | 1 | 1390 | -0.679 | [-1.576, 0.195] |
| SOXX | sw_semiconductor / gap | 0 | 1643 | 6.007 | [3.402, 9.359] |
| SOXX | sw_semiconductor / post_open | 0 | 1643 | 0.109 | [-0.313, 0.483] |
| SOXX | sw_semiconductor / gap | 1 | 1634 | -0.202 | [-0.547, 0.103] |
| SOXX | sw_semiconductor / post_open | 1 | 1634 | -0.040 | [-0.494, 0.395] |
| SOXX | 512480 / next_tradable_open | 0 | 1398 | -0.140 | [-0.846, 0.555] |
| SOXX | 512480 / next_tradable_open | 1 | 1390 | -0.614 | [-1.407, 0.174] |

## 年度稳定性

SOX 各年 MSE 改善（%）；d0/d1 分别为延迟0/1，2026年只到10月16日：

| Year | SW gap d0 | SW post-open d0 | SW gap d1 | SW post-open d1 | ETF d0 | ETF d1 |
| --- | --- | --- | --- | --- | --- | --- |
| 2020 | 3.049 | 0.107 | 0.359 | 0.025 | — | — |
| 2021 | 9.697 | 0.375 | -1.620 | 0.248 | 0.813 | -1.346 |
| 2022 | 5.923 | 0.213 | 0.079 | -0.367 | 0.376 | -1.278 |
| 2023 | -0.982 | 0.820 | -0.731 | -0.037 | 0.212 | 0.249 |
| 2024 | 1.090 | -0.087 | 0.092 | 0.267 | -0.078 | 0.215 |
| 2025 | 0.151 | -0.271 | -0.629 | 0.141 | -0.797 | 0.117 |
| 2026 | 14.767 | -0.075 | -0.013 | -0.348 | -0.650 | -1.141 |

开盘缺口改善并不均匀：2023年为负，2024/2025年较小，2026年较大。延迟0的年度缺口区间只有2020、2021、2026年完全大于零，其余跨零。外部诊断保留了所有代理、目标和延迟的逐年结果及区间。三个高度相关的海外代理方向相近，不等于三次独立重复实验。不能只展示正年份，也不能用某个交易代理改善掩盖 ETF 的负 MSE 结果。

## ETF 费用与延迟情景

以下为每个回放行的平均收益，单位基点。Gross 是零费用；其他列依次扣往返5/10/20/40基点，每次实际单边换仓扣一半。`global` 是基准，`theme_residual` 是增强模型。

| Theme | Delay | Model | Gross mean bp/day | Net 5 bp | Net 10 bp | Net 20 bp | Net 40 bp |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SOX | 0 | global | 10.725 | 9.566 | 8.407 | 6.089 | 1.454 |
| SOX | 0 | theme_residual | 9.965 | 8.810 | 7.655 | 5.344 | 0.723 |
| SOX | 1 | global | 7.110 | 6.048 | 4.986 | 2.861 | -1.388 |
| SOX | 1 | theme_residual | 9.411 | 8.284 | 7.158 | 4.904 | 0.398 |
| SMH | 0 | global | 10.725 | 9.566 | 8.407 | 6.089 | 1.454 |
| SMH | 0 | theme_residual | 9.294 | 8.143 | 6.991 | 4.688 | 0.081 |
| SMH | 1 | global | 7.110 | 6.048 | 4.986 | 2.861 | -1.388 |
| SMH | 1 | theme_residual | 9.788 | 8.643 | 7.499 | 5.210 | 0.632 |
| SOXX | 0 | global | 10.725 | 9.566 | 8.407 | 6.089 | 1.454 |
| SOXX | 0 | theme_residual | 9.629 | 8.489 | 7.348 | 5.066 | 0.502 |
| SOXX | 1 | global | 7.110 | 6.048 | 4.986 | 2.861 | -1.388 |
| SOXX | 1 | theme_residual | 9.312 | 8.193 | 7.073 | 4.834 | 0.356 |

所有情景均回放1,398行；延迟1的 MSE 比较只有1,390个预测行。缺预测的回放行默认期望空仓，但持仓限制可能保留原仓位。因此两种统计的分母不同，本次保留现有行为并明确披露。

SOX 延迟0增强模型毛均值9.965低于基准10.725基点，往返10基点后为7.655对8.407；延迟1则反过来，增强模型毛均值9.411高于基准7.110，净均值7.158高于4.986，尽管其 MSE 更差。因此“尚无稳健ETF改善”并不表示每个交易代理都为负，而是综合预测损失、延迟敏感性、年度波动与任意的正负号仓位规则，尚不能确认可部署优势。往返40基点时，SOX 两种模型、两种延迟的复合收益都为负；延迟1增强模型的算术均值虽为正，也不例外。完整复合收益、夏普、回撤、暴露及交易次数在外部诊断中。

回放仅做多或空仓，保留连续持仓，次日才可卖出并计末端清仓费；开盘涨跌停与前期成交额限制采用100万元预算、前期ADV的1%。这些近似没有验证排队成交、真实滑点或容量。开盘缺口解释能力也不能证明开盘后仍能捕获该收益。

## 来源与复现

原始记录归数据平台所有，任务标识为 `overseas-theme-source-20261029`。相对于配置的数据根目录，原始记录在 `quant-market-data-platform/research/tasks/overseas-theme-source-20261029`，研究结果在 `quant-market-research/tasks/overseas-theme-source-20261029`。`source_receipt.json` 记录每个原文件SHA256、参数、时间、版本及QA；`price_semantics_review.json` 记录单位和调整口径；`artifact_receipt.json` 记录归档文件哈希；`existing_controls_inventory.json` 记录控制输入范围及哈希。仓库没有复制供应商原始行、原始价格、私有绝对路径或逐日预测。

外部保留了 `reproduce_source_probe.py` 和 `reproduce_experiment.py`。这些脚本使用固定任务路径；新取数应先保留旧回执并改用新的外部任务目录，不能当作安全的覆盖接口。源数据获取仍归数据所有者，公开研究 runner 只读取审查输入。原始文件、规范化主题输入和脚本通过外部归档哈希关联。

| Theme | Input manifest SHA256 |
| --- | --- |
| SOX | f29e702cfbfb8476c51136e31cc06ce0ef9a5d52e3334f2893cf0276a30938ca |
| SMH | 7e6dfd992ececd3c722394d433bc6144647553b3e6b21d74c93aff93b9b65319 |
| SOXX | e7e0a4688ef714c4217e26aaf5cb73b9f43741674369ddeba4501c237b7f2ed8 |

```bash
# Resolve these roots from machine-local workspace settings; do not store credentials here.
export OWNER_TASK="$DATA_ROOT/quant/quant-market-data-platform/research/tasks/overseas-theme-source-20261029"
export STUDY_TASK="$DATA_ROOT/quant/quant-market-research/tasks/overseas-theme-source-20261029"
# From a clean checkout of 5122f1abd54bc69037631a4d45f8e28c24a29647:
PYTHONPATH=src python -m market_research.studies.overseas_leadlag.theme \
  --manifest "$STUDY_TASK/sox_reviewed_manifest.json" \
  --output "$STUDY_TASK/new-sox-reproduction"
```

SMH/SOXX 改用对应的审查清单和全新输出目录。需使用包含现有依赖的环境。runner 重核验每个输入文件、清单字节和实际生成代码版本；各 `research_diagnostics.json` 记录清单摘要。上面的代码 SHA 是实际运行版本，后续文档提交由 Git 历史与集成报告记录，不能混用。

## Alpaca 与结论边界

**没有实际测试 Alpaca。** 只检查了四个预期环境变量是否存在，结果均不存在；所检查的项目与共享说明也未指出已配置的加载接口。没有读取凭证内容，没有登录、改订阅、交易或更改账户。

官方历史日线接口说明了分页、`raw/split/dividend/spin-off/all` 调整及 feed 选择；FAQ 区分单交易所 IEX 与合并 SIP，并说明历史访问依赖账户权限。文档不能证明当前账户的权限、实际覆盖或返回价格。将来实际测试需明确核对 feed、调整、分页、标的覆盖及日线时间戳口径；股票接口不保证支持 ^SOX。

结果仍为 `retrospective_exploratory`、`historical_pit_certified: false`。当前检索及最终历史拆股分红口径不是历史获取版本。没有全新保留样本、历史选样证明、独立供应商交叉验证、多重检验校正、历史延迟实测或成交与容量证明。没有修改生产模型、冻结 forward-v1、网页选用项、共享 current/latest 或生产数据。

本次查阅的供应商一手文档：

- [yfinance PriceHistory parameters](https://ranaroussi.github.io/yfinance/reference/yfinance.price_history.html)
- [Alpaca historical stock bars](https://docs.alpaca.markets/us/reference/stockbars)
- [Alpaca market-data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq)
