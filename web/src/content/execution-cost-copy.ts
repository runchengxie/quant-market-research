export const executionCostCopy = {
  "title": [
    "A-share trading costs and capacity",
    "A股交易成本与策略容量"
  ],
  "stage": [
    "L2 sample audited · static costs measured locally",
    "L2样本已审计 · 静态成本已在本地测量"
  ],
  "conclusion": [
    "A three-day L2 pilot is now measured. Time encoding and one-sided books must be checked before interpreting static execution costs.",
    "三日L2探索已完成首轮测量。时间编码与单边盘口须先核对，静态成本才能正确解释。"
  ],
  "scope": [
    "Sample: 2026-04-16, 2026-04-24 and 2026-07-20; a deterministic Shanghai/Shenzhen security subset. Static cost figures remain local pending vendor permission for aggregate derivatives. No actual-order or dynamic-impact calibration is claimed.",
    "样本为2026-04-16、2026-04-24与2026-07-20的沪深证券确定性子样本。静态成本数值先保留本地，待确认聚合衍生结果的公开许可；尚无真实委托或动态冲击校准。"
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
  ],
  "auditTitle": [
    "First local sample audit",
    "首轮本地样本审计"
  ],
  "auditScope": [
    "65,673,625 source rows scanned. Code modulo 37 selects stock-like Shanghai/Shenzhen prefixes; the earliest source timestamp in each continuous-trading security-minute is retained. This is a convenience pilot, not a probability sample or point-in-time eligibility screen.",
    "共扫描65,673,625行源快照。按沪深股票代码前缀与数值代码模37筛选，每个连续竞价证券分钟选最早源时间戳。这是便利性探索样本，不是概率抽样，也未完成时点证券资格核验。"
  ],
  "auditCounts": [
    "100,236 sampled snapshots across 427 selected security-days; 98,072 valid two-sided books across 426 security-days. The 2,164 exclusions are one-sided books. Date and clock checks cover all source rows; detailed book checks cover only sampled snapshots.",
    "427个选中证券日共选出100,236条分钟快照；其中426个证券日的98,072条为有效双边盘口，另有2,164条单边盘口被排除。日期与时钟检查覆盖全部源记录，详细盘口检查仅覆盖抽样快照。"
  ],
  "auditClock": [
    "Some lake copies encode time_ms as milliseconds relative to 09:30. A renamed TickTime is not automatically an HHMMSSmmm clock. This run used sources with explicit native SecuCode and TickTime columns and rejected mere aliases.",
    "部分数据湖副本的time_ms是相对09:30的毫秒数。把它改名为TickTime，不等于完成HHMMSSmmm时钟转换。本次使用含原生SecuCode与TickTime的源文件，拒绝仅靠别名推断时钟。"
  ],
  "auditFiltering": [
    "The earlier 2026-04-24 canonical pilot has 403,373 fewer snapshot rows than its source. Empty-level filtering can alter the sampled population; this study therefore retained the source rows and logged exclusions explicitly. Original files and published aliases were unchanged.",
    "已有2026-04-24标准层pilot比源文件少403,373条快照。空档位过滤可能改变样本分布，因此本次保留源记录并明确记录剔除原因；原始文件和发布别名保持不变。"
  ],
  "auditNext": [
    "Static buy/sell curves for CNY 10k, 100k, 1m and 10m have been computed with full-depth coverage and a matched-population comparison. Missing depth is never extrapolated. Next: confirm publication terms, add point-in-time eligibility and lagged liquidity groups, and expand preselected dates before calibration.",
    "已在本地计算1万、10万、100万和1000万元的静态买卖成本曲线，同时报告十档覆盖率与同一批盘口的规模对照，深度不足不外推。下一步确认发布条款，补充时点证券资格与滞后流动性分组，并按预先确定的日期扩展样本。"
  ]
} as const;
