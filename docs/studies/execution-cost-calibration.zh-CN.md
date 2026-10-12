# 真实订单执行成本校准入口

[English](execution-cost-calibration.md)

已实现标准订单导入、报价对齐、成本分解和按日期留出验证。80笔母单、20个日期的合成数据已跑通整个流程；它只验证程序，没有提供实盘滑点证据。本专题尚未收到可用的真实委托回报，真实订单校准和自身因果冲击识别仍未完成。

这部分是研究诊断，不新增执行模拟器。供应商字段适配仍由数据平台负责，通用执行模型仍由quant-platform负责。

## 私有输入

在仓库外准备`manifest.json`和`orders`、`fills`、`quotes`三个文件，每类只提供一个CSV或Parquet。价格用元、数量用股，时间必须带明确时区。声明模式为`ashare_execution_costs.canonical_orders.v1`，并指定：`data_kind`为`actual`、`paper`或`synthetic`；`source`记录来源；`price_unit`为`CNY`；`quantity_unit`为`share`；`time_contract`为`explicit_UTC_offset`；`fees_contract`为`actual_parent_total_CNY_once`。

| 文件 | 必填字段 | 口径 |
| --- | --- | --- |
| orders | parent_order_id,symbol,side,target_qty,decision_time,arrival_time,end_time,state,fees_cny | 一行对应完整母单；方向为buy/sell；结束状态为filled/cancelled/expired/rejected。税费填写实际母单总额，只计一次。 |
| fills | fill_id,parent_order_id,fill_time,qty,price | 保留部分成交；成交编号唯一，且必须关联母单。零成交文件保留表头。 |
| quotes | symbol,quote_time,bid,ask | 唯一双边报价；可另提供available_time记录实际接收时间，market_level提供同期市场基准。 |

可选订单字段`predicted_arrival_bp`与`prediction_time`接收事前模型预测，预测时间不得晚于到达时间。时间检查不能证明模型训练过程没有未来信息，仍需审查预测来源。未提供报价接收时间时，程序明确假设行情时间就是可用时间，尚不能验证传输延迟。

先在私有适配层还原母单、子单、改量和最终状态，不把同一母单的子单当成独立样本。无法关联时保留为待核实。标准文件不包含账号或凭证，原始回报和来源记录继续留在私有目录。

## 如何计算

买入方向记为+1、卖出为−1。完整执行损耗包括三项：成交价格相对决策时中间价的偏离、未成交数量按结束时中间价计算的机会成本、实际税费。分母是目标股数乘决策中间价，再换算为基点。

相对到达价的成交成本用实际成交均价计算；决策到到达的价格变化单列。零成交没有成交均价指标，但保留机会成本。结果可以为负，也包含市场与信号本身的价格变化，不能全部解释为自己的冲击。

只采用事件时点之前已经可用的报价，默认最大报价年龄为1000毫秒。缺失、过期报价会使完整校准不可用，订单仍保留，不借用未来报价、插值或日收盘价。结束后30、300、1800秒的市场调整响应，以订单结束时中间价为基准，扣除市场基准对数收益；缺少相应行情时留空。结束可能是撤单或失效，不一定是最后成交。

训练和验证按完整UTC到达日期分开，母单不会跨集合。若训练母单在首个验证订单到达时尚未结束，会从训练样本剔除，避免借用未来成交结果。先用训练样本的分方向成本中位数作为基线，报告后续样本的平均绝对误差、偏差和绝对误差90分位数。默认至少20笔训练母单和10笔验证母单；验证中出现未训练的方向时不强行评估。真实、模拟盘与合成数据不能混合训练。公开方向分组及每个指标至少保留20个有效样本；这是样本诊断，不是总体置信区间。

## 运行与发布

```bash
PYTHONPATH=src uv run --locked python scripts/run_execution_cost_calibration.py \
  --input-root "$PRIVATE_ORDER_INPUT" --output-root "$NEW_EXTERNAL_RUN" \
  --max-quote-age-ms 1000 --min-group-orders 20
```

输出目录必须为新目录。逐母单测量、详细验证和校验码留在仓库外；`aggregate.json`只包含固定方向分组与允许公开的汇总指标，不包含订单编号、证券、事件时间或机器路径。发布前核实数据来源与证据类型。

`actual_order_calibrated`只有在输入声明为真实订单、且按日期的基线评估完成时才可能成立，含义仅限这一观测成本基线。来源真实性、因果冲击、排队模型和资金容量仍是不同门槛。

后续应按订单金额／此前成交额、参与率、波动率、价差、执行时长和执行方式建模，并与这个简单基线做样本外比较。先使用日常交易已有的回报。本任务不下新订单；若以后开展执行方式对照实验，需另外明确分配方式、市场控制与识别方案。
