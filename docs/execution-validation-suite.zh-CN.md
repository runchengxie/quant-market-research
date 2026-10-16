# 风险规则验证与执行诊断

[English](execution-validation-suite.md)

本轮固定1元规则，继续检查收益变化来自哪里、换一年是否仍有效，以及卖出对执行条件有多敏感。实验沿用现有研究流程，原18组公开结果保持不变。

[冻结协议](execution-validation-protocol.json)记录规则、窗口、完整执行参数和评价指标。2024年规则是在看到失败案例后提出的；2025年的原有研究和本次覆盖筛查也已经看过，因此只能称为回顾性的跨年验证，不能称为未见样本的样本外验证。后续不会用2025年结果挑选参数。

2024年分别比较原基准、仅价格过滤、仅新增ST可得时间检查、仅终止公告过滤及组合规则。各组采用同一套四只股票的非现金减值声明。2025年拆分价格和ST检查；终止公告来源覆盖尚不完整，该规则明确未测试。空事件表不能证明公告证据齐全。

准备输入保留完整选股股票池，并逐值核对原入选行情和目标。2025年的日线清单与旧准备版本不同，专用流程只在原入选行情及基准目标完全一致后，允许明确记录这项清单变化；其他来源校验继续保留。这不能证明当时未留存的完整候选池历史字节完全一致。

逐股票账务拆分交易现金、已付及未付股息、股票权益、期末持股价值和费用。两组的差额用于说明收益由哪些股票贡献，不能当成“保持其他持仓不变”的因果估计。退出诊断分别统计卖出尝试、成交和残留股数；停牌、价格限制、参与率约束可以重叠，不能据此给每张过期订单指定唯一原因。

压力情景改变资金规模、成交量参与率、释放窗口和批次数。它们检验分钟行情模型的敏感性，尚未建模排队、集合竞价、盘口补充或策略自身的市场冲击，不能直接得出实盘容量。

自动预检查核对输入哈希、完整股票池留存、交易日覆盖、目标时间、行情、公司行动和来源绑定。实际回放仍须通过持仓净值完整性和权益归属检查，再由独立账务诊断核对结果。通过检查不代表历史数据已达到不可修订的PIT标准。

当实际执行输入、参数、估值声明和执行引擎哈希完全一致时，允许经过验证后复用不可变台账。回执会标明`verified_ledger_reuse`并引用原记录，不会把复用结果冒充新增独立模拟。

## 本轮结果

低价过滤的收益改善没有在第二年复现。2024年主要改善来自避开两只后来无法正常退出的股票；ST可得时间检查和终止公告过滤单独启用，均没有改变本样本的实际成交结果。2025年价格与ST规则没有改变目标或成交，因此没有增量收益。

下表均为全年分钟行情回放的账户收益，已经扣除模型费用。2024年四只股票使用同一套非现金全额减值假设，减值保留股数，不制造卖出现金；2025年未验证终止公告规则。

| 年份与规则 | 100万元 | 1000万元 |
| --- | ---: | ---: |
| 2024 基准、仅ST、仅终止公告 | 4.7317% | 3.6037% |
| 2024 仅价格、组合规则 | 12.3079% | 11.1010% |
| 2025 基准、仅价格、仅ST、价格与ST | 70.2800% | 72.6307% |

2024年100万元账户的改善约75,762元：两只避开股票的毛损益改善约47,360元，其他替换与再平衡约28,874元，新增费用抵减约472元。1000万元账户对应约749,736元：476,509元、277,884元及费用抵减4,657元。原有002621持仓没有因此消失。这是守恒的账务拆分，不证明两个风险股票解释了全部收益差，也不证明过滤规则具有普遍预测能力。

## 执行压力情景

以下全部使用2024年组合规则与相同减值声明。除另列项目外，资金1000万元、参与率5%、释放窗口330分钟、单批释放、延迟1分钟。完成率按目标名义金额计算；它不是订单数量完成率，也不是实盘容量。

| 情景 | 账户收益 | 目标金额完成率 |
| --- | ---: | ---: |
| 对照 | 11.1010% | 89.7397% |
| 参与率1% | 14.5060% | 80.5644% |
| 参与率3% | 12.4459% | 89.2028% |
| 参与率10% | 10.9268% | 90.1199% |
| 30分钟窗口 | 11.7348% | 85.6801% |
| 120分钟、5批释放 | 12.0231% | 86.5211% |
| 1亿元 | 14.7280% | 74.7599% |

收益与成交完成率没有同向变化。减少成交会改变现金、持仓和买卖时点，碰巧提高这一段样本的收益；1亿元收益更高也不能证明容量更大。不能从这些回放里挑选一个“最优”执行参数，再声称它已通过验证。模型未估计自身订单对行情的反作用。

退出诊断保留了002621的65次失败卖出尝试及期末残留股数：100万元账户13,900股、1000万元账户138,500股。全额减值后的账面零价值不等于成功退出。窗口内价格限制、可成交量和释放时间用于记录可观察约束，多个约束可以同时存在；没有订单的日期不应算作持续卖出尝试。

市场环境补充采用前一交易日可见指标：成交额前5日均值低于前20日均值的80%，或主板股票前日收盘跌停比例至少2%。2024年低流动性标签5天、前日跌停压力标签26天，其中1天重叠；2025年分别0天和4天。每年最初20天缺少窗口内历史，明确留空。标签可能落在暴跌后的反弹日，不能把该组收益解释成暴跌当日表现。

## 复现与下一步

本轮24条情景记录包含12次实际模拟、12次经过哈希校验的台账复用。相同目标和执行输入的规则组共享经济结果，不能把24条记录当作24次独立实验。原18组公开结果不替换。

按项目数据契约提供外部数据根目录和原准备目录，在锁定的研究环境及正式分钟执行引擎中运行。输出目录须为新的独立目录，不能覆盖原始数据或共享结果：

```bash
PYTHONPATH=src python scripts/prepare_execution_validation_suite.py \
  --data-root "$PLATFORM_DATA" --base-prepared "$BASE_PREPARED" \
  --output "$PREPARATION_ROOT" --protocol docs/execution-validation-protocol.json \
  --source-packet "$SOURCE_PACKET" --mode combined \
  --profile fees_1m --profile fees_10m
PREPARED="$PREPARATION_ROOT/combined"
python - "$PREPARED" <<'PYPROFILES'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
inputs = json.loads((root / 'inputs.json').read_text())
(root / 'requested-profiles.json').write_text(json.dumps(
    inputs['experiment_study']['authorized_profiles'], indent=2) + '\n')
PYPROFILES
PYTHONPATH=src python scripts/run_execution_validation_suite.py \
  --output "$PREPARED" --profiles "$PREPARED/requested-profiles.json"
PYTHONPATH=src python scripts/prepare_execution_stress_profiles.py \
  --prepared "$PREPARED" --output "$STRESS_PREPARED" --profile fees_100m
PYTHONPATH=src python scripts/run_execution_validation_suite.py \
  --output "$STRESS_PREPARED" --profiles "$STRESS_PREPARED/requested-profiles.json"
PYTHONPATH=src python scripts/prepare_execution_market_regimes.py \
  --prepared "$PREPARED" --output "$REGIME_PREPARED"
```

2025年使用`baseline`、`price_only`、`st_only`或`price_st`，不提供2024公告包；若日线来源清单发生本轮已核验的变更，必须显式使用`--allow-daily-manifest-revision`，同时仍须通过原入选行情和目标逐值核对。诊断入口是`diagnostics.analyze_run`，配对归因是`analysis_summary.compare_reports`，环境分组是`analysis_summary.market_regime_summary`；它们属于研究工具，不是实盘下单接口。

下一步应先补齐2025年公告证据，再预先固定规则检验真正未见的时间段。历史数据修订安全、退市后可交易报价、排队与自身市场冲击仍待解决。本轮检查不能替代这些证据。

后续数据缺口与前瞻留样方案见[下一阶段说明](execution-validation-next-stage.zh-CN.md)及[冻结评估协议](execution-validation-followup-protocol.json)。
替代批次的启动条件和仓库外逐日归档契约见[前瞻登记与归档说明](execution-validation-holdout-archive.zh-CN.md)。
