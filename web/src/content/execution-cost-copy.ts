export const executionCostCopy = {
  "title": [
    "A-share trading costs and capacity",
    "A股交易成本与策略容量"
  ],
  "stage": [
    "Scenario baseline · L2 calibration pending",
    "情景基线 · Level-2 校准待完成"
  ],
  "conclusion": [
    "At 60% daily one-way turnover, illustrative fees alone total 10.5% per year; each additional 1 bp per side adds 3 percentage points.",
    "日均单边换手60%时，示例显性费用简单年化为10.5%；买卖每侧滑点再增加1bp，年成本增加3个百分点。"
  ],
  "scope": [
    "Scope: arithmetic scenarios only, with no securities or date sample. These are not observed A-share slippage estimates or compounded return losses.",
    "样本范围：仅有算术情景，没有证券与日期样本。这不是A股实测滑点，也不是复利净值损失。"
  ],
  "question": [
    "How much predicted return survives execution, and how does this change with capital and turnover?",
    "预测收益在实际执行后能保留多少，资金规模与换手率如何改变结果？"
  ],
  "baseline": [
    "Turnover definitions and cost sensitivity",
    "换手定义与成本敏感性"
  ],
  "assumptions": [
    "Illustrative assumptions: 250 sessions, constant NAV, no leverage, 1 bp inclusive commission on each side and 5 bp sell-side tax. Confirm the fee date and broker invoice before use; do not add included levies again. 1 bp = 0.01%.",
    "示例假设：250个交易日、净值固定、无杠杆，买卖综合佣金各1bp，卖出税费5bp。使用前核对费率适用日期与交割单，佣金已含的规费不要重复添加。1bp = 0.01%。"
  ],
  "formula": [
    "Annual cost = days × [buy turnover × (buy fees + buy slippage) + sell turnover × (sell fees + sell slippage)]. Rates use decimals.",
    "年成本 = 交易日数 × [买入换手 ×（买入费用 + 买入滑点）+ 卖出换手 ×（卖出费用 + 卖出滑点）]。费率使用小数。"
  ],
  "definition": [
    "For balanced fully invested rebalances without flows: one-way turnover = half of the sum of absolute weight changes. A 60% sum means about 30% buying and 30% selling.",
    "无资金流且满仓平衡调仓时：单边换手 = 权重变化绝对值之和的一半。绝对值之和60%，约对应买入30%、卖出30%。"
  ],
  "slippage": [
    "Slippage on each side (bp)",
    "每侧滑点（bp）"
  ],
  "oneway": [
    "60% buying + 60% selling",
    "买入60% + 卖出60%"
  ],
  "twoway": [
    "30% buying + 30% selling",
    "买入30% + 卖出30%"
  ],
  "boundary": [
    "Slippage must use a named benchmark. Midpoint-based book walking already includes half-spread and depth cost: do not add spread or the same impact twice. Unfilled orders and opportunity costs require a separate ledger.",
    "滑点必须指定参考价格。相对中间价的静态吃单已含半价差与深度成本，不要再重复叠加价差或同一冲击。未成交与机会成本需要单独记账。"
  ],
  "evidence": [
    "What Level-2 can establish",
    "Level-2 能支持什么证据"
  ],
  "snapshots": [
    "Ten-level snapshots: measure quoted spread, depth and static buy/sell curves. Report P50/P90/P95 and depth coverage. Insufficient depth means incomplete coverage, never extrapolated fills.",
    "十档快照：测量报价价差、深度和静态买卖成本曲线，报告P50/P90/P95与深度覆盖率。深度不足须标记未完整覆盖，不能外推成交。"
  ],
  "events": [
    "Orders and trades: validate event order, units, cancellation links and zero-price semantics before estimating signed flow or price response. Historical replay cannot identify the causal impact of a fictional order.",
    "逐笔委托与成交：先验证事件顺序、单位、撤单关联与零价格事件语义，再估计订单流和价格响应。历史回放无法识别虚构订单自身的因果冲击。"
  ],
  "fills": [
    "Actual order and fill reports: calibrate implementation shortfall against the decision price, including partial fills, cancellations, fees and unfilled quantity. No such calibration is published here yet.",
    "真实委托与成交回报：以决策价校准执行差额，覆盖部分成交、撤单、费用和未成交量。本专题尚未发布这种校准结果。"
  ],
  "roadmap": [
    "Next experiments and publication gates",
    "后续实验与发布条件"
  ],
  "phase1": [
    "1 · Baseline: reconcile dated fees and cost ledgers with quant-platform; audit embedded slippage to prevent double charging. Separate turnover of a portfolio from trading activity of a stock.",
    "1 · 成本基线：对齐quant-platform的分期费率与成本账本，审计内置滑点以防重复扣费。组合换手率与个股交易活跃程度须分开。"
  ],
  "phase2": [
    "2 · L2 pilot: inspect local schema and coverage through quant-market-data-platform. Stratify by size, liquidity, volatility, session and market state; publish aggregate cost surfaces with exclusion rates and day/stock-clustered uncertainty.",
    "2 · L2小样本：通过quant-market-data-platform核对本地字段与覆盖率。按规模、流动性、波动、时段和市场状态分组，公开聚合成本曲面、剔除比例及按日期/证券聚类的不确定性。"
  ],
  "phase3": [
    "3 · Strategy sensitivity: compare gross, fee-only and modeled net returns at CNY 10m/100m/1bn. Map position-level orders to participation; test buffers, rebalance frequency and execution speed with signal decay, T+1, limits and suspensions. These are planned scenarios, not measured capacity.",
    "3 · 策略敏感性：在1000万元、1亿元、10亿元情景下比较毛收益、仅扣费收益与模型净收益。逐股映射参与率，比较缓冲调仓、频率和执行速度，并纳入信号衰减、T+1、涨跌停和停牌。这些是计划情景，尚非实测容量。"
  ],
  "gate": [
    "Publish only after semantic checks, sample manifests, benchmark definitions, exclusions and time-based out-of-sample validation are reviewable. Raw vendor data and order records stay outside this repository.",
    "语义核验、样本清单、基准定义、剔除规则及按时间划分的样本外验证可审查后，才发布实证结论。供应商原始数据和委托记录保留在仓库外。"
  ],
  "sources": [
    "Methods, related evidence and reading",
    "方法、关联证据与阅读"
  ],
  "literature": [
    "The linked papers are a reading queue, not a calibration dataset. Full texts and historical fee assumptions still need review; no quoted cost parameter is adopted here.",
    "以下论文是待精读线索，不是校准数据。全文与历史费率假设仍需核对，本专题未采纳其中的成本参数。"
  ],
  "method": [
    "Study protocol and data requirements",
    "专题协议与数据要求"
  ],
  "microcap": [
    "Existing micro-cap execution diagnostic",
    "现有微盘执行诊断"
  ],
  "liquidity": [
    "Cross-market liquidity context",
    "跨市场流动性背景"
  ]
} as const;
