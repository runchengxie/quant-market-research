# Quant Market Research 研究说明

[English page](index.md)

这里介绍公开因子研究目前发现了什么、数字怎样计算，以及哪些问题还没有答案。读专题时可以先看开头的白话结论，再用表格和方法说明核对细节。

中英文页面使用各自独立的稳定 URL。可以通过页面顶部的语言链接切换版本，也可以直接分享对应页面地址。

每个专题会先说明目前能得出的结论，再列关键数字、证据限制和下一步。页面保留完整研究细节，遇到缩写和专业词时会先解释它们与结论的关系。

## 因子研究

- [小微盘 ST 口径审计](research/experiments/microcap-st-comparability-audit-20261018.zh-CN.md)：逐版本核对历史资格、退市退出、权重及成本，不能把市值尾部剔除当作 ST 对照。
- [低估值口径与当前样本](research/experiments/valuation-denominators-20261018.zh-CN.md)：五种分母、六家公司当前快照计算及尚未完成的历史检验。
- [公开研究收口状态](research-closeout-status.zh-CN.md)：查看已完成的核对、仍待补充的数据或人工验证，以及各状态的含义。
- [PB 与 ROE：怎样比较估值和盈利能力](research/factors/pb-roe.zh-CN.md)：在同一批候选股票中，加入盈利能力指标后，历史对照发生了什么变化。
- [低换手：它可能反映哪些特征](research/factors/low-turnover.zh-CN.md)：低换手可能和什么特征同时出现，控制这些特征后收益差还剩多少。
- [微盘股：收益证据与水下时间](research/factors/microcap.zh-CN.md)：按历史规则重建的小市值组合经历过多大跌幅、多久才回到前高。
- [微盘组合公共执行模拟诊断](research/experiments/microcap-execution-diagnostic-20260928.zh-CN.md)：把短期样本放进模拟交易流程后，哪些订单成交、哪些限制了结果。
- [2008–2014 年小市值成交活跃度补充](research/factors/smallcap-turnover-history.zh-CN.md)：早年小市值股票的成交额大致如何，数据能说明什么。
- [Barra 风格因子字典](research/factors/barra-factor-dictionary.zh-CN.md)：公开研究中各类风格指标的含义，以及它们与商业模型的边界。
- [Barra 风格研究资料清单](research/factors/barra-source-inventory.zh-CN.md)：哪些支撑材料可以公开用于研究。

网页负责展示图表和交互，说明站提供因子研究的方法、数据口径和证据限制。网站构建方式、实施计划和运行手册属于维护资料，不作为公开研究内容。

## 因子研究发布去向

历史研究结果用于支持进一步调查，不构成投资建议，也不代表未来收益。

独立市场研究项目及其可复现方法、样本定义、结果和限制放在本站。[Quant Factor Observatory](https://runchengxie.github.io/quant-factor-observatory/) 负责因子目录组织、标准化因子专题、发布状态和符合其发布契约的审核投影。同一主题同时出现在两站时，以专题页或发布 manifest 中的来源身份为准，链接到权威材料，不复制整份内容。私有策略研究仍由 `quant-research` 维护；公开发布需要单独审核并生成脱敏投影。

- [低估值历史覆盖与排名](research/experiments/valuation-panel-20261018.zh-CN.md)：130 个月份，先核对缺失与共同样本，再比较排名。
- [小微盘含 ST / 剔除 ST 成对探索](research/experiments/microcap-st-paired-short-window-20261018.zh-CN.md)：短窗口结果与覆盖选择限制。
- [海外信号真实时点归档协议](research/experiments/overseas-forward-v1.zh-CN.md)：固定信号与实际收据，尚未积累合格前向样本。
