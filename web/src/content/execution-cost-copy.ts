export const executionCostCopy = {
  "title": [
    "A-share trading costs and capacity",
    "A股交易成本与策略容量"
  ],
  "stage": [
    "Static L2 pilot · published",
    "静态L2探索 · 已公开"
  ],
  "conclusion": [
    "At CNY 100k, median static buy/sell costs are about 8.5 bp in this sample. At CNY 1m, full ten-level coverage falls to about 64%/67%.",
    "本样本中，10万元订单的静态买卖成本中位数约8.5bp；到100万元，十档完整覆盖率降至约64%/67%。"
  ],
  "scope": [
    "Sample: 2026-04-16, 2026-04-24 and 2026-07-20; 98,072 valid two-sided security-minute books from a deterministic Shanghai/Shenzhen subset. These are descriptive static measurements; actual-order and dynamic-impact calibration remain incomplete.",
    "样本为2026-04-16、2026-04-24与2026-07-20的沪深证券确定性子样本，共98,072条有效双边证券分钟盘口。这是描述性静态测量，真实委托与动态冲击仍待校准。"
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
    "Aggregate publication permission was confirmed by the owner on 2026-10-12. Next: add point-in-time eligibility and lagged liquidity groups, and expand preselected dates before calibration.",
    "研究者于2026-10-12确认已获得聚合结果公开许可。下一步补充时点证券资格与滞后流动性分组，并按预先确定的日期扩展样本后再校准。"
  ],
  "resultsTitle": [
    "Static costs and ten-level coverage",
    "静态成本与十档覆盖率"
  ],
  "resultsNote": [
    "Reference notional = midpoint × target shares. Fractional analytical shares are allowed; these are not cash budgets or lot-sized executable orders. Costs are relative to the current midpoint, include half-spread and depth consumption, and exclude fees, latency and causal impact.",
    "参考名义规模 = 中间价 × 分析股数；允许分析用的非整手股数，不是现金预算或真实整手委托。成本相对当前中间价，含半价差与吃档，不含税费、延迟和自身因果冲击。"
  ],
  "conditionalTitle": [
    "Cost conditional on full ten-level coverage",
    "仅在十档完整覆盖时的成本"
  ],
  "coverageTitle": [
    "Full coverage among valid two-sided books",
    "有效双边盘口的完整覆盖率"
  ],
  "selectionWarning": [
    "Each size has a different fully covered population. Read cost quantiles with coverage and sample counts: the uncovered orders have missing full-order costs, not zero costs.",
    "不同规模能完整覆盖的样本不同。成本分位数须与覆盖率和样本数一起看；未覆盖订单的完整成本是缺失值，不是零。"
  ],
  "matchedTitle": [
    "Compare order sizes using the same books",
    "在同一批盘口中比较订单规模"
  ],
  "matchedNote": [
    "The common subset contains 8,480 snapshots where both buy and sell orders at every size are fully covered. It helps separate size effects from changing populations, but remains a selected subset and does not establish strategy capacity.",
    "共同子样本包含8,480条快照，买卖所有规模均能完整覆盖。它帮助区分订单规模与样本变化的影响，但仍是筛选后的子集，不能据此认定策略容量。"
  ],
  "download": [
    "Download reviewed aggregate JSON",
    "下载经审查的聚合JSON"
  ],
  "extraTitle": [
    "Daily and depth-group comparisons",
    "按日与深度分组比较"
  ],
  "extraNote": [
    "The three dates are not a continuous time series. Depth groups use same-day median ten-level value; they are not market-cap groups or lagged signals. All quantiles are snapshot-weighted sample distributions, not population confidence intervals.",
    "三个日期不是连续时间序列。深度组按同日十档金额中位数划分，不是市值组，也不是滞后信号。所有分位数按快照计权，描述样本分布，不是全市场置信区间。"
  ],
  "buy": [
    "Buy",
    "买入"
  ],
  "sell": [
    "Sell",
    "卖出"
  ],
  "size": [
    "Reference notional (CNY)",
    "参考名义规模（元）"
  ],
  "count": [
    "Fully covered books",
    "完整覆盖盘口数"
  ],
  "side": [
    "Side",
    "方向"
  ],
  "coverage": [
    "Full coverage",
    "完整覆盖率"
  ],
  "costUnit": [
    "Cost vs midpoint (bp)",
    "相对中间价成本（bp）"
  ],
  "coverageUnit": [
    "Fully covered books (%)",
    "完整覆盖盘口（%）"
  ],
  "logAxis": [
    "Notional increases tenfold at each step",
    "每档名义规模扩大10倍"
  ],
  "p50": [
    "P50 cost (bp)",
    "P50成本（bp）"
  ],
  "p90": [
    "P90 cost (bp)",
    "P90成本（bp）"
  ],
  "p95": [
    "P95 cost (bp)",
    "P95成本（bp）"
  ],
  "day": [
    "Day / depth group",
    "日期 / 深度组"
  ],
  "books": [
    "Valid books",
    "有效盘口数"
  ],
  "spread": [
    "Median quoted spread (bp)",
    "报价价差中位数（bp）"
  ],
  "shallow": [
    "Shallow",
    "浅档组"
  ],
  "middle": [
    "Middle",
    "中档组"
  ],
  "deep": [
    "Deep",
    "深档组"
  ],
  "tick10k": [
    "10k",
    "1万"
  ],
  "tick100k": [
    "100k",
    "10万"
  ],
  "tick1m": [
    "1m",
    "100万"
  ],
  "tick10m": [
    "10m",
    "1000万"
  ],
  "matchedValues": [
    "Exact values for the common subset",
    "共同样本的完整数值"
  ]
} as const;
