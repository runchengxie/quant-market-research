# A股交易成本、市场冲击与策略容量

[English](README.md) · [公开专题](https://runchengxie.github.io/quant-market-research/research/execution-costs/)

当前结论：十个选定交易日共有306,483条有效双边证券分钟盘口。10万元订单的静态买卖成本中位数为9.27/8.87bp，100万元订单十档完整覆盖率为62.12%/67.68%。早期深市订单引用候选匹配率约99.7%，但所选早期沪市样本没有订单。18组受成交与资金约束的策略情景已完成；这些结果仍不能校准真实滑点或证明实盘容量。

[扩展研究报告](../../docs/research/experiments/execution-cost-expansion-20261012.zh-CN.md) · [可复现核验笔记本](expansion_review.ipynb) · [此前三日发现](pilot_findings.zh-CN.md)

250个交易日、每天买卖各占净值60%、示例综合佣金各1bp、卖出税费5bp时，年费用支出与固定净值之比为10.5%。每侧滑点增加1bp，年成本增加3个百分点。若60%指买卖合计，上述数字减半。这是简单支出比例，不是复利收益扣减；费率是情景输入，尚非核实后的当前收费表。

[研究方法](methodology.md)、[数据要求](data_requirements.md)、[文献队列](literature_review.md)与[专题声明](study.yml)记录后续校准协议。网页集中展示结论、口径与限制；本目录保存可复现方法，避免到处重复证据。

数据平台负责供应商标准化与L2治理；quant-platform负责通用执行模拟与成本归因；本仓库负责实证研究与审查后的聚合结果。校准完成后，因子观测站可展示净收益与容量摘要并链接主专题。

复现时先在仓库外复制[输入示例](expansion.spec.example.json)，核实时间、价格和数量单位，再绑定本地源路径。[英文协议](README.md#reproduce-with-private-inputs)列出测量、复核、策略与聚合发布命令。运行结果与已执行笔记本保存在外部数据目录；公开页面只使用审查后的聚合结果。
