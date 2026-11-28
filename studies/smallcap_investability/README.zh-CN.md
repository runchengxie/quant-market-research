# 小微盘研究完整待办清单

[English](README.md)

状态表示交付进展，不表示投资有效性。完成可以只指一项有边界的诊断完成，不认证时点数据、可成交Alpha或假设成立。

复核日期：2026-11-29

机器可读来源为[task-registry.json](task-registry.json)。“等待证据”表示所列门槛尚未满足，不表示所有相关数据都不存在。本清单不创建定时任务或前瞻注册。

| 编号 | 优先级 | 状态 | 任务 | 依赖 |
| --- | --- | --- | --- | --- |
| [SC-001](#sc-001) | P0 | 已完成限定交付 | 固定保留来源与版本 | — |
| [SC-002](#sc-002) | P0 | 部分完成 | 解释120日窗口复现差异 | SC-001 |
| [SC-003](#sc-003) | P0 | 等待证据 | 认证历史入选资格 | SC-001 |
| [SC-004](#sc-004) | P0 | 部分完成 | 核对价格与公司行动 | SC-001 |
| [SC-005](#sc-005) | P0 | 等待证据 | 固定缺价与退市处理 | SC-003, SC-004 |
| [SC-006](#sc-006) | P0 | 已完成限定交付 | 明确共同交易时点契约 | SC-001 |
| [SC-007](#sc-007) | P0 | 已完成限定交付 | 构建三组共同支持的目标名单 | SC-001 |
| [SC-008](#sc-008) | P0 | 部分完成 | 扩展共同份额与现金账本 | SC-006, SC-007 |
| [SC-009](#sc-009) | P1 | 等待证据 | 比较三组配对多头净账户 | SC-003, SC-004, SC-005, SC-008 |
| [SC-010](#sc-010) | P1 | 部分完成 | 版本化公开风格描述符契约 | SC-001 |
| [SC-011](#sc-011) | P1 | 等待证据 | 恢复历史行业版本 | SC-003 |
| [SC-012](#sc-012) | P1 | 已完成限定交付 | 测量归档最终持仓暴露 | SC-001 |
| [SC-013](#sc-013) | P2 | 等待证据 | 核对已实现因子收益归因 | SC-008, SC-010, SC-011 |
| [SC-014](#sc-014) | P3 | 等待证据 | 验证协方差与特质风险预测 | SC-013 |
| [SC-015](#sc-015) | P1 | 部分完成 | 检验低换手的增量信息 | SC-007, SC-012 |
| [SC-016](#sc-016) | P2 | 等待证据 | 检验头部校准与单调性 | SC-003, SC-005, SC-010 |
| [SC-017](#sc-017) | P2 | 部分完成 | 运行K与权重强度对照 | SC-009, SC-012 |
| [SC-018](#sc-018) | P2 | 部分完成 | 区分持有缓冲与信号平滑 | SC-007, SC-008 |
| [SC-019](#sc-019) | P1 | 部分完成 | 审计执行时钟与订单证据 | SC-001 |
| [SC-020](#sc-020) | P1 | 等待证据 | 估计匹配成本情景与校准 | SC-008, SC-019 |
| [SC-021](#sc-021) | P1 | 部分完成 | 预定义压力事件与对照 | SC-001 |
| [SC-022](#sc-022) | P1 | 等待证据 | 重放固定持仓的压力退出 | SC-003, SC-005, SC-008, SC-019, SC-021 |
| [SC-023](#sc-023) | P2 | 等待证据 | 绘制资金、参与率与退出容量 | SC-020, SC-022 |
| [SC-024](#sc-024) | P2 | 等待证据 | 审计历史财务覆盖 | SC-003 |
| [SC-025](#sc-025) | P2 | 等待证据 | 运行市场特征剔除实验 | SC-009, SC-010, SC-016 |
| [SC-026](#sc-026) | P2 | 等待证据 | 增量检验质量与估值 | SC-024, SC-025 |
| [SC-027](#sc-027) | P0 | 部分完成 | 起草统一的前瞻协议 | SC-001 |
| [SC-028](#sc-028) | P1 | 已完成限定交付 | 规定配对推断与试验登记 | SC-001 |
| [SC-029](#sc-029) | P0 | 已完成限定交付 | 维护经过依赖检查的任务登记 | SC-001 |
| [SC-030](#sc-030) | P1 | 部分完成 | 发布并持续维护证据地图 | SC-029 |

<a id="sc-001"></a>
## SC-001 · 固定保留来源与版本

P0 · 已完成限定交付 · quant-market-research

验收：登记哈希、日期，区分86／134／136期样本。

下一步：新增证据时继续保留原版本身份。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md) · [source 2](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/low-turnover.md)

<a id="sc-002"></a>
## SC-002 · 解释120日窗口复现差异

P0 · 部分完成 · quant-market-research

验收：恢复生成代码、输入与支持度规则，解释7.60%、4.22%、6.26%的差异，不挑选有利版本。

下一步：核对具名重放收据，区分找到了文件与恢复了原始运行。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/low-turnover.md)

<a id="sc-003"></a>
## SC-003 · 认证历史入选资格

P0 · 等待证据 · quant-market-data-platform

验收：每个形成日名单有时点来源、版本、ST、上市及交易资格证据。

下一步：审查历史名单资产，保留未解决的资格分类。

未满足门槛：仅凭归档评分不能认证历史入选资格。

<a id="sc-004"></a>
## SC-004 · 核对价格与公司行动

P0 · 部分完成 · quant-market-research

验收：原始／复权价格、股数、现金能跨拆并股、分红与异常跳变核对。

下一步：优先核对2008至2016年未解决跳变，保留无法匹配的事件。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-005"></a>
## SC-005 · 固定缺价与退市处理

P0 · 等待证据 · quant-market-research

验收：所有入选持仓留在账本，未知估值不静默置零或换股。

下一步：将区间估值、结算政策绑定到可审计来源版本。

未满足门槛：完整历史终值与区间覆盖尚未认证。

<a id="sc-006"></a>
## SC-006 · 明确共同交易时点契约

P0 · 已完成限定交付 · quant-market-research

验收：所有比较明确形成、最早决策／执行、T+1及估值区间。

下一步：数据及账本门槛通过后，再按已写规范实施。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-investability-protocol-draft.md)

<a id="sc-007"></a>
## SC-007 · 构建三组共同支持的目标名单

P0 · 已完成限定交付 · quant-market-research

验收：基准、高换手剔除与低换手选择共用不依赖未来结果的股票池／支持集，并核对权重及缺失。

下一步：将保留目标与支持集剔除记录交给账本就绪检查。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-target-support-20261128.md)

<a id="sc-008"></a>
## SC-008 · 扩展共同份额与现金账本

P0 · 部分完成 · quant-market-research

验收：使用共享提供方，在获准历史上核对仓位、现金、费用、公司行动、失败与终值。

下一步：复用已有账本试点，按时点及历史输入门槛扩展。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-009"></a>
## SC-009 · 比较三组配对多头净账户

P1 · 等待证据 · quant-market-research

验收：相同日期、资格、账本、执行和成本政策，并列多空两腿及相对基准净结果。

下一步：账本获准后再运行基准、剔除与低换手账户。

未满足门槛：目标名单已生成，经过认证的全历史配对账户尚未完成。

<a id="sc-010"></a>
## SC-010 · 版本化公开风格描述符契约

P1 · 部分完成 · quant-market-research

验收：逐项登记滞后、单位、方向、缩尾、标准化股票池与覆盖。

下一步：区分归档代理与可重新生成的规模、贝塔、波动、流动性描述符。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-011"></a>
## SC-011 · 恢复历史行业版本

P1 · 等待证据 · quant-market-data-platform

验收：形成日行业归属可追溯，未知行业暴露保持可见。

下一步：在归因使用行业变量前审计历史修订。

未满足门槛：归档Top 50行业未知权重不可忽略，当前分类不能替代历史。

<a id="sc-012"></a>
## SC-012 · 测量归档最终持仓暴露

P1 · 已完成限定交付 · quant-market-research

验收：共同日期比较原始／残差信号与K，保留广市场、局部基准及描述符缺失。

下一步：将已测得的尾部暴露反向纳入持仓层检查要求。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-013"></a>
## SC-013 · 核对已实现因子收益归因

P2 · 等待证据 · quant-market-research

验收：滞后暴露、可识别市场／行业回归与账户区间能核对贡献及残差；复用quant-platform接口。

下一步：分别纳入不含换手与含换手的两套模型。

未满足门槛：完整对齐的暴露、行业及账户区间尚未获准。

<a id="sc-014"></a>
## SC-014 · 验证协方差与特质风险预测

P3 · 等待证据 · quant-market-research

验收：仅用过去数据估计，检验滚动预测／实现风险、覆盖及压力校准。

下一步：归因核对后，另立预测验证实验。

未满足门槛：暴露诊断或解释性回归不是经验证的风险预测。

<a id="sc-015"></a>
## SC-015 · 检验低换手的增量信息

P1 · 部分完成 · quant-market-research

验收：共同支持／日期比较低波动、活跃度、非流动性及避开高换手的作用，保留原始控制。

下一步：配对三组账户，做剔除实验及控制顺序敏感性。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/low-turnover.md) · [source 2](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-target-support-20261128.md)

<a id="sc-016"></a>
## SC-016 · 检验头部校准与单调性

P2 · 等待证据 · quant-market-research

验收：预定义互斥排名区间及周期，报告配对不确定性和收益重叠处理。

下一步：将冻结排名与获准未来标签对齐，不剔除失败持仓。

未满足门槛：当前暴露面板没有获准的未来收益标签。

<a id="sc-017"></a>
## SC-017 · 运行K与权重强度对照

P2 · 部分完成 · quant-market-research

验收：按预定网格在匹配风险、成本、资格下比较，报告稳定区域而非历史最优格。

下一步：净账户获准后扩展现有仅暴露的K对照。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-018"></a>
## SC-018 · 区分持有缓冲与信号平滑

P2 · 部分完成 · quant-market-research

验收：固定信号及日期，分开报告净收益、目标变化、实际换手与残差风险。

下一步：以历史缓冲记录作开发证据，再构造配对账本案例。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/low-turnover.md)

<a id="sc-019"></a>
## SC-019 · 审计执行时钟与订单证据

P1 · 部分完成 · quant-market-research

验收：决策、到达报价、成交、费用、未成交库存具有已验证的单位及时钟语义。

下一步：扩展两日期适用性检查，不宣称普遍覆盖。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-020"></a>
## SC-020 · 估计匹配成本情景与校准

P1 · 等待证据 · quant-market-research

验收：区分费用、价差、冲击、延迟并避免重复收费；情景假设与真实校准分开。

下一步：先做配对账户情景，匹配执行证据获准后才拟合冲击。

未满足门槛：现有报价／账户情景不足以确立经券商执行校准的成本。

<a id="sc-021"></a>
## SC-021 · 预定义压力事件与对照

P1 · 部分完成 · quant-market-research

验收：在查看结果前固定市场／规模回撤事件规则，保留正常对照，并与低ADV月份区分。

下一步：必需输入、账户及时钟证据获准后再审查冻结草案，不将历史重标为前瞻。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-investability-protocol-draft.md)

<a id="sc-022"></a>
## SC-022 · 重放固定持仓的压力退出

P1 · 等待证据 · quant-market-research

验收：冻结事件前持仓，在整个期限保留停牌、缺失、未售库存及现金。

下一步：先检查事件前目标、分钟数据及库存是否获准，再模拟退出。

未满足门槛：事件前合格持仓及对齐的可执行观测仍需获准。

<a id="sc-023"></a>
## SC-023 · 绘制资金、参与率与退出容量

P2 · 等待证据 · quant-market-research

验收：按资金、参与率、期限报告净收益、成本、未成交库存和退出时间，不把ADV当容量。

下一步：整个网格使用相同成本和压力退出来源版本。

未满足门槛：容量结论依赖获准的执行与压力证据。

<a id="sc-024"></a>
## SC-024 · 审计历史财务覆盖

P2 · 等待证据 · quant-market-data-platform

验收：公告时点版本及亏损、负净资产、缺报告规则覆盖目标微盘股票池。

下一步：按日期和规模测量覆盖，将2020年后受限质量样本分开保留。

未满足门槛：现有质量诊断主要覆盖2020年以后前800只股票。

<a id="sc-025"></a>
## SC-025 · 运行市场特征剔除实验

P2 · 等待证据 · quant-market-research

验收：规模、换手、波动、反转／动量在配对预测或净组合结果中有增量，并报告不确定性。

下一步：扩展因子库前先评价少量固定因子组。

未满足门槛：先满足净账户与未来标签契约。

<a id="sc-026"></a>
## SC-026 · 增量检验质量与估值

P2 · 等待证据 · quant-market-research

验收：使用匹配的时点覆盖，区分复合质量与子项，不重复计入杠杆。

下一步：覆盖及基线剔除实验获准后再加入财务因子组。

未满足门槛：不能从历史19因子快照推断财务覆盖。

<a id="sc-027"></a>
## SC-027 · 起草统一的前瞻协议

P0 · 部分完成 · quant-market-research

验收：明确协议名、冻结日、模型、支持集、配置、成本、终点及修订政策，核对历史12／24期规则。

下一步：必需输入、账户及时钟证据获准后再审查冻结草案，不将历史重标为前瞻。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-investability-protocol-draft.md)

<a id="sc-028"></a>
## SC-028 · 规定配对推断与试验登记

P1 · 已完成限定交付 · quant-market-research

验收：记录全部尝试、重叠周期、分块／HAC选择和多重比较，不挑最优格。

下一步：数据及账本门槛通过后，再按已写规范实施。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-investability-protocol-draft.md)

<a id="sc-029"></a>
## SC-029 · 维护经过依赖检查的任务登记

P0 · 已完成限定交付 · quant-market-research

验收：每项有编号、归属、优先级、状态、验收、依赖、下一步；完成项关联已有证据。

下一步：只随经审查的证据变化更新状态。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/studies/smallcap_investability/task-registry.json)

<a id="sc-030"></a>
## SC-030 · 发布并持续维护证据地图

P1 · 部分完成 · quant-market-research

验收：双语网站展示优先级、当前证据、未满足门槛及下一步，并保留来源身份。

下一步：发布当前固定来源快照，实际研究门槛变化后再更新。

已有证据：[source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)
