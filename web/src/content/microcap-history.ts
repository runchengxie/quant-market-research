import type { LocalText } from './microcap-hub';
// Explicit editorial publication allowlist. Never load restricted sources at build time.
export const historyReviewedOn = '2026-10-16';
export type HistoryRecord = { id: string; title: LocalText; scope: LocalText; status: LocalText; finding: LocalText; boundary: LocalText };
export const microcapHistory: HistoryRecord[] = [
  {
    "id": "H01",
    "title": [
      "Size across market regimes",
      "规模与市场阶段"
    ],
    "scope": [
      "2008–2026 · 223 month ends",
      "2008—2026 · 223 个月末"
    ],
    "status": [
      "Historical association",
      "历史关联"
    ],
    "finding": [
      "Industry-demeaned factor spreads vary across regimes. Size is defined in the large-cap direction; a negative spread cannot be described as small-cap underperformance.",
      "行业去均值后的因子收益差随阶段变化。规模因子按大盘方向定义，负收益差不能解释为小盘跑输。"
    ],
    "boundary": [
      "The claim that 2026 was the first positive large-cap year conflicts with positive years listed in the same record. Early fundamentals are reconstructed; 2026 is incomplete.",
      "“2026 是首次大盘占优年份”与同一记录列出的其他正收益年份冲突。早期基本面为重建值，2026 年尚不完整。"
    ]
  },
  {
    "id": "H02",
    "title": [
      "Early multi-factor spread stability",
      "早期多因子收益差稳定性"
    ],
    "scope": [
      "Overlapping starts in 2019–2022, ending in 2026",
      "2019—2022 年重叠起点，结束于 2026 年"
    ],
    "status": [
      "Exploratory comparison",
      "探索性对照"
    ],
    "finding": [
      "Selected long-short combinations appeared stable across several starts. These are overlapping histories rather than independent tests.",
      "部分多空组合在几个起点下较稳定，但这些历史区间相互重叠，不是独立检验。"
    ],
    "boundary": [
      "A factor that helped a long-short spread need not help a long-only account. Keep selected model weights restricted and require a frozen future comparison.",
      "对多空收益差有帮助的因子未必改善纯多头账户。具体模型权重保留在受限记录中，后续需要冻结规则的前瞻对照。"
    ]
  },
  {
    "id": "H03",
    "title": [
      "Minimum-cap threshold and endpoint reversal",
      "最低市值门槛与终点反转"
    ],
    "scope": [
      "Historical windows ending in 2026",
      "以 2026 年为终点的历史窗口"
    ],
    "status": [
      "Endpoint-sensitive",
      "对终点敏感"
    ],
    "finding": [
      "An attractive minimum-cap filter depended on the ending period. Changing the endpoint weakened the original interpretation.",
      "最低市值过滤曾表现较好，但改变终点后，原来的解释不再稳固。"
    ],
    "boundary": [
      "Neither a permanent size floor nor unrestricted micro-cap exposure is established as the long-run optimum.",
      "既不能据此确立长期最低市值门槛，也不能反向证明完全放开微盘敞口最优。"
    ]
  },
  {
    "id": "H04",
    "title": [
      "Long-only translation and universe choice",
      "纯多头转译与股票池选择"
    ],
    "scope": [
      "2008–2026; separate post-2015 universe",
      "2008—2026；另有 2015 年后股票池"
    ],
    "status": [
      "Historical simulation",
      "历史模拟"
    ],
    "finding": [
      "Long-short findings did not transfer mechanically to long-only portfolios. Results changed materially with the universe and starting date.",
      "多空发现无法直接搬到纯多头组合；股票池和起始时间改变后，结果明显不同。"
    ],
    "boundary": [
      "Early unadjusted returns and incomplete eligibility require repair. A broad-universe result cannot certify a more restricted investable universe.",
      "早期未复权收益和不完整资格筛选仍需修复。全市场结果不能替代更窄可投资股票池的验证。"
    ]
  },
  {
    "id": "H05",
    "title": [
      "Broad factor-combination search",
      "大规模因子组合搜索"
    ],
    "scope": [
      "455 combinations of 14 factors",
      "14 个因子的 455 种组合"
    ],
    "status": [
      "Selection-sensitive search",
      "受筛选影响的搜索"
    ],
    "finding": [
      "The historical search found attractive selected combinations, with substantial drawdowns and weaker later-period results.",
      "历史搜索找到了一些较好的组合，同时伴随较大回撤和后期走弱。"
    ],
    "boundary": [
      "The selected winner is not independent proof of optimal synergy. Conflicting annualizations and an inconsistent yearly win count remain unresolved.",
      "搜索胜出者不能独立证明最优协同。不同记录的年化口径、逐年胜率计数存在未解决的不一致。"
    ]
  },
  {
    "id": "H06",
    "title": [
      "Combined scores versus independent sleeves",
      "合成评分与独立子组合"
    ],
    "scope": [
      "2016–August 2026",
      "2016 年至 2026 年 8 月"
    ],
    "status": [
      "Construction sensitivity",
      "组合构造敏感性"
    ],
    "finding": [
      "A combined-score screen exceeded separate sleeves in the inspected history; much of the advantage appeared after 2021.",
      "在已查看历史中，合成评分筛选优于独立子组合，优势较多来自 2021 年以后。"
    ],
    "boundary": [
      "Full-sample selection prevents a strict out-of-sample claim. Match the eligibility, cash, costs and execution clock before selecting a construction.",
      "使用全样本选型不能称为严格样本外。选择构造方法前需统一资格、现金、成本与执行时点。"
    ]
  },
  {
    "id": "H07",
    "title": [
      "Capital and traded-amount unit corrections",
      "资金规模与成交额单位修正"
    ],
    "scope": [
      "Separate 2019–2026 execution checks",
      "独立的 2019—2026 年执行检查"
    ],
    "status": [
      "Corrected assumptions",
      "假设已修正"
    ],
    "finding": [
      "Capital assumptions and a 1,000-fold traded-amount unit error changed earlier liquidity interpretations. A high simulated fill ratio followed the correction.",
      "资金假设和成交额单位的千倍错误改变了早期流动性解释；修正后模拟成交率较高。"
    ],
    "boundary": [
      "A high fill ratio under an assumed model does not establish unconstrained liquidity or calibrated market impact.",
      "假设模型下的高成交率不能证明流动性没有约束，也不能替代市场冲击校准。"
    ]
  },
  {
    "id": "H08",
    "title": [
      "Model attribution and equal-weight benchmark",
      "模型归因与等权基准诊断"
    ],
    "scope": [
      "2025–2026 attribution; 2016–2026 benchmark",
      "2025—2026 年归因；2016—2026 年基准"
    ],
    "status": [
      "Diagnostic, incomplete evidence",
      "诊断性证据，尚不完整"
    ],
    "finding": [
      "Style covariance explained part of a model return series. A separate equal-weight benchmark diagnosis exposed universe, new-listing and return-clipping defects.",
      "风格协方差解释了模型收益的一部分；另一项等权基准诊断发现股票池、新股和收益截断问题。"
    ],
    "boundary": [
      "Covariance is not causal skill attribution. Revised benchmarks still zero-filled missing stock-days and omitted costs; they cannot establish model promotion.",
      "协方差不是因果能力归因。修订基准仍对缺失股票日填零且未计成本，不能据此决定模型晋级。"
    ]
  },
  {
    "id": "H09",
    "title": [
      "Small-cap × low-turnover screening",
      "小盘 × 低换手初筛"
    ],
    "scope": [
      "2015–July 2026; development through 2023",
      "2015 年至 2026 年 7 月；开发段截至 2023 年"
    ],
    "status": [
      "Historical exploration",
      "历史探索"
    ],
    "finding": [
      "Raw, residualized and combined screens gave different results and large drawdowns. Public candidate and cadence tables are retained below.",
      "原始、残差化与复合筛选结果不同，回撤普遍较大；公开候选与调仓表保留在后文。"
    ],
    "boundary": [
      "The repeatedly inspected 2024+ segment is descriptive. Narrative and snapshot versions differ; do not splice them into a single final backtest.",
      "反复查看的 2024 年后样本属于描述性证据。叙述与快照版本不同，不能拼接成一份最终回测。"
    ]
  },
  {
    "id": "H10",
    "title": [
      "Turnover definition sensitivity",
      "换手率定义敏感性"
    ],
    "scope": [
      "2008–July 2026; 223 formations",
      "2008 年至 2026 年 7 月；223 次形成"
    ],
    "status": [
      "Historical cross-section",
      "历史截面"
    ],
    "finding": [
      "Point-in-time turnover and prior-window means or medians answer different questions. Quintile diagnostics are separate from later decile controls.",
      "时点换手率与过去窗口的均值、中位数回答不同问题；五分组诊断也不同于后来的十分组控制。"
    ],
    "boundary": [
      "Alternative definitions require their own executable comparison. Definition sensitivity alone does not identify a unique premium.",
      "替代定义仍需各自的可执行对照；定义敏感性不能确立唯一溢价。"
    ]
  },
  {
    "id": "H11",
    "title": [
      "Deconfounding: early and corrected controls",
      "去混杂：早期与修正后的控制"
    ],
    "scope": [
      "Early 133 formations; later 86 common-support months",
      "早期 133 次形成；后续 86 个共同样本月份"
    ],
    "status": [
      "Conditional association",
      "条件关联"
    ],
    "finding": [
      "Later matched-stock controls retained a low-turnover association after size, risk, liquidity and return controls. A regression check also remained positive.",
      "后续在共同股票样本中控制规模、风险、流动性和过去收益后，低换手关联仍为正，回归检查也为正。"
    ],
    "boundary": [
      "Earlier anatomy tables use a different sample and ranking basis. Neither double sorts nor regressions identify a causal or executable premium.",
      "早期分解表的样本与排序口径不同。双重排序和回归都不能单独证明因果或可执行溢价。"
    ]
  },
  {
    "id": "H12",
    "title": [
      "Frozen prospective observation",
      "冻结规则的前瞻观察"
    ],
    "scope": [
      "One completed month: August 2026",
      "仅一个已完成月份：2026 年 8 月"
    ],
    "status": [
      "One-month observation",
      "单月观察"
    ],
    "finding": [
      "The frozen July-end signal produced opposite raw and controlled spreads in August. Only one completed month is reported by the reviewed source.",
      "7 月末冻结信号在 8 月产生方向相反的原始与控制后收益差；已审查来源只报告了一个已完成月份。"
    ],
    "boundary": [
      "Do not mark later pending months complete merely because time has passed. Require actual receipts and multiple new observations.",
      "不能因为日历已翻页就把后续待完成月份改为完成；需要实际记录和更多新增观察。"
    ]
  },
  {
    "id": "H13",
    "title": [
      "Daily investability and intraday coverage",
      "逐日可投资性与日内覆盖"
    ],
    "scope": [
      "Separate daily portfolio and intraday samples",
      "独立的逐日组合与日内样本"
    ],
    "status": [
      "Simulation; partial coverage",
      "模拟；覆盖不完整"
    ],
    "finding": [
      "An explicit suspension correction lowered the daily simulation’s annual return from 7.04% to 5.33%. Minute coverage was about 80.8%; quote-level coverage was lower.",
      "明确计入停牌后的逐日模拟年化由 7.04% 降至 5.33%。分钟覆盖约 80.8%，逐笔报价覆盖更低。"
    ],
    "boundary": [
      "Missing quotes are not proven suspensions or zero returns. Incomplete minute and order-book records cannot support a full-history fill-cost replay.",
      "缺价不能自动当作停牌或零收益。不完整的分钟和盘口记录不足以支持全历史成交成本重放。"
    ]
  },
  {
    "id": "H14",
    "title": [
      "Window × cadence comparisons",
      "窗口 × 调仓频率对照"
    ],
    "scope": [
      "Public snapshot: 3 windows and 16 grid cells",
      "公开快照：3 个窗口、16 个矩阵单元"
    ],
    "status": [
      "Historical sensitivity",
      "历史敏感性"
    ],
    "finding": [
      "The complete published grid is available, alongside three fixed monthly low-turnover windows. Definitions and engine scope differ between the tables.",
      "完整公开矩阵与三个固定月频低换手窗口均已保留，但两表的定义和引擎范围不同。"
    ],
    "boundary": [
      "A source caveat says the grid was pending while the same snapshot contains 16 rows. Preserve the inconsistency and inspect actual rows; do not infer independent confirmation.",
      "来源提示曾称矩阵待生成，但同一快照已有 16 行。应保留这项不一致并查看实际行，不能推定已独立确认。"
    ]
  },
  {
    "id": "H15",
    "title": [
      "Weight targets, shares and cash reconciliation",
      "权重目标、份额与现金核对"
    ],
    "scope": [
      "Monthly and biweekly ledgers",
      "月频与双周份额账本"
    ],
    "status": [
      "Unreconciled comparison",
      "比较尚未核齐"
    ],
    "finding": [
      "Weight-level, ideal-share and continuous-ledger results differ. Formation counts, target counts and owner replay periods also differ.",
      "权重层、理想份额与持续账本结果不同，形成次数、目标次数和重放期数也不同。"
    ],
    "boundary": [
      "Do not splice return series or declare one canonical result. Zero modeled impact is an assumption, not evidence of zero realized cost.",
      "不能拼接收益序列或直接指定唯一权威结果。模拟冲击为零是设定，不是实际成本为零的证据。"
    ]
  },
  {
    "id": "H16",
    "title": [
      "Capital, lots and delayed fills",
      "资金、整手与延迟成交"
    ],
    "scope": [
      "Seven public capital scenarios; separate lot checks",
      "七档公开资金情景；另有整手检查"
    ],
    "status": [
      "Path-dependent simulation",
      "依赖路径的模拟"
    ],
    "finding": [
      "Cash, lot rounding and delayed orders changed outcomes. The published capital sweep has rising returns at larger capital.",
      "现金、整手取整和延迟订单会改变结果；公开资金扫描中，较大资金对应较高模拟收益。"
    ],
    "boundary": [
      "This is not an economic capacity curve: deferred orders can skip later losers, and impact is uncalibrated. Opportunity-cost figures are diagnostic.",
      "这不是经济意义上的容量曲线：延迟订单可能避开后续下跌标的，冲击也未校准。机会成本数字只能作为诊断。"
    ]
  },
  {
    "id": "H17",
    "title": [
      "Monthly micro-cap exclusion scorecard",
      "月频微盘排除记分卡"
    ],
    "scope": [
      "2015–July 2026; selected monthly 40-name results",
      "2015 年至 2026 年 7 月；选定的月频 40 只结果"
    ],
    "status": [
      "Source-reported historical results",
      "来源报告的历史结果"
    ],
    "finding": [
      "Removing different bottom-cap fractions did not produce a monotonic improvement; large drawdowns remained.",
      "排除不同比例的最小市值股票并未带来单调改善，大回撤仍然存在。"
    ],
    "boundary": [
      "A selected scorecard is not completion of the full weighting, buffer, cost and capacity protocol. Restricted configurations are not republished.",
      "选定记分卡不代表完整的权重、缓冲、成本和容量协议已完成。受限配置不在公开页重新发布。"
    ]
  },
  {
    "id": "H18",
    "title": [
      "Monthly 100-name and weekly 200-name proxies",
      "月频 100 只与周频 200 只代理"
    ],
    "scope": [
      "Different 2015+ and 2023+ samples",
      "分别使用 2015 年后与 2023 年后样本"
    ],
    "status": [
      "Historical bundles recovered; partial provenance",
      "历史结果包已找回；来源链不完整"
    ],
    "finding": [
      "The dated monthly 100-name bundle was recovered through a documented storage migration; its stored full-sample summary agrees with the rounded source-note figures. The weekly 200-name proxy remains a separate comparison.",
      "通过有记录的存储迁移找回了月频 100 只结果包，存储的全样本摘要与来源笔记的四舍五入数值一致。周频 200 只代理仍是独立对照。"
    ],
    "boundary": [
      "No performance was rerun. The recent-window comparison receipt and immutable code/input/output binding remain missing. A separate weekly proxy cumulative-excess label still fails percentage-point subtraction; do not pool or reinterpret these returns.",
      "没有重跑业绩。近期窗口对照记录，以及不可变的代码、输入、输出绑定仍缺失。另一项周频代理的累计超额标签仍与百分点相减不符，不能合并或擅自重解释这些收益。"
    ]
  },
  {
    "id": "H19",
    "title": [
      "Complete exclusion robustness protocol",
      "完整排除稳健性协议"
    ],
    "scope": [
      "Bottom 0/10/20/30%; weighting and buffer controls",
      "排除底部 0/10/20/30%；权重与缓冲对照"
    ],
    "status": [
      "Outputs recovered; structural checks passed",
      "输出已找回；结构检查通过"
    ],
    "finding": [
      "The migrated bundle contains 112 factor rows, 56 weighting comparisons, 80 buffer rows and 24 capacity rows. The factor, buffer and capacity grids have unique keys, no blank cells and complete declared axes; four checkpoint files match final outputs byte-for-byte.",
      "迁移后的结果包含 112 行因子、56 行权重对照、80 行缓冲和 24 行容量记录。因子、缓冲与容量矩阵的组合键唯一，无空白单元，声明的维度完整；四个检查点文件与最终输出逐字节相同。"
    ],
    "boundary": [
      "The recorded owner-code commit fields are unknown. This artifact audit does not rerun performance, authenticate every historical input, establish an untouched holdout or promote a strategy. The separate characteristic-decomposition protocol still has no located result bundle.",
      "结果记录的所属代码提交字段为 unknown。本次产物审计没有重跑业绩，也没有认证全部历史输入、确立未查看的留出样本或使策略晋级。独立的特征分解协议仍未找到结果包。"
    ]
  },
  {
    "id": "H20",
    "title": [
      "Characteristic decomposition protocol",
      "特征分解协议"
    ],
    "scope": [
      "Size, illiquidity, extreme returns, volatility and quality",
      "规模、非流动性、极端收益、波动与质量"
    ],
    "status": [
      "Protocol only",
      "仅研究方案"
    ],
    "finding": [
      "Double sorts and regression designs would test which characteristics accompany the apparent micro-cap effect.",
      "双重排序与回归设计用于检验哪些特征伴随着表面的微盘效应。"
    ],
    "boundary": [
      "No verified outputs were found for this protocol. Mechanism claims remain open, including delisting and shell-value effects.",
      "未找到该协议已核实的输出。机制解释仍待检验，包括退市和壳价值影响。"
    ]
  },
  {
    "id": "H21",
    "title": [
      "Future-quote and current-membership repair",
      "未来报价与当前成分筛选修复"
    ],
    "scope": [
      "2015–September 2026 validity audit",
      "2015 年至 2026 年 9 月有效性审计"
    ],
    "status": [
      "Replay blocked",
      "重放受阻"
    ],
    "finding": [
      "Earlier targets used future quote availability and current membership. Removing these filters changes the sample and invalidates direct reuse of old results.",
      "旧目标曾使用未来报价可得性与当前成分筛选；移除后样本改变，旧结果不能直接复用。"
    ],
    "boundary": [
      "A current membership snapshot cannot reconstruct historical membership. Missing held-security marks block a complete validated NAV.",
      "当前成分快照不能重建历史成分；持仓证券缺失计价会阻断完整、经验证的净值。"
    ]
  },
  {
    "id": "H22",
    "title": [
      "Historical names, ST status and date parsing",
      "历史名称、ST 状态与日期解析"
    ],
    "scope": [
      "Historical-status supplement, September 2026",
      "2026 年 9 月历史状态补充"
    ],
    "status": [
      "Data repair, not return evidence",
      "数据修复，不是收益证据"
    ],
    "finding": [
      "Historical names replace current-name ST inference. Strict date parsing exposed nullable export strings and previously admitted delisted securities.",
      "历史名称用于替代按当前名称推断 ST；严格日期解析发现空值导出字符串和此前误纳入的退市证券。"
    ],
    "boundary": [
      "A documented nullable adapter repairs representation only. Suspension-event matches do not prove a tradable price or settlement value.",
      "有依据的空值适配只修复数据表达。匹配停牌事件不能证明存在可交易价格或结算价值。"
    ]
  },
  {
    "id": "H23",
    "title": [
      "Frozen target re-formation",
      "冻结规则后的目标重建"
    ],
    "scope": [
      "Protocol frozen before new performance inspection",
      "协议先于新业绩检查冻结"
    ],
    "status": [
      "Targets rebuilt; NAV unverified",
      "目标已重建；净值未核实"
    ],
    "finding": [
      "Historical eligibility is reconstructed without future-price filters; unknown status stays unknown. Old-target audits and new targets remain separate.",
      "重建历史资格时不再使用未来价格筛选，未知状态仍保留为未知；旧目标审计与新目标分开。"
    ],
    "boundary": [
      "Targets are not a validated account. Do not drop missing-price names and renormalize; engine installation and run verification need separate receipts.",
      "目标集合不等于已验证账户。不能删除缺价标的再归一化；引擎安装与运行验证需要各自记录。"
    ]
  },
  {
    "id": "H24",
    "title": [
      "400-name missing-quote audit",
      "400 只组合缺价审计"
    ],
    "scope": [
      "Multiple audits with different windows",
      "多次审计，窗口不同"
    ],
    "status": [
      "Incomplete valuation",
      "计价不完整"
    ],
    "finding": [
      "Public audits found 189 missing marks on 117 dates in one window; an older broader replay found 3,708 marks on 1,407 dates.",
      "一个窗口的公开审计发现 117 个日期、189 条缺价；另一段更宽旧重放发现 1,407 个日期、3,708 条缺价。"
    ],
    "boundary": [
      "Counts are neither distinct delistings nor comparable rates without denominators. Remaining-name averaging silently renormalizes exposure; the return bias is not quantified.",
      "这些不是独立退市数量，没有分母也不能直接比较缺失率。对剩余股票求均值会隐含重分配敞口，收益偏差尚未量化。"
    ]
  },
  {
    "id": "H25",
    "title": [
      "Early history, cleaned sources and recovery",
      "早期历史、清洗来源与回本等待"
    ],
    "scope": [
      "2008–2014 extension; later overlapping sources",
      "2008—2014 年扩展；后续重叠来源"
    ],
    "status": [
      "Historical return and risk",
      "历史收益与风险"
    ],
    "finding": [
      "The longer history adds earlier drawdowns and prolonged underwater intervals. Cleaned and earlier source series are shown separately.",
      "延长历史补充了早期回撤和较长水下期；清洗来源与早期序列分开展示。"
    ],
    "boundary": [
      "Do not stitch sources without an overlap audit. An unfinished recovery is censored at the sample endpoint rather than assigned a completed waiting time.",
      "没有重叠审计就不能拼接来源。样本末仍未回本的区间应标为尚未结束，不能当成已完成等待时长。"
    ]
  },
  {
    "id": "H26",
    "title": [
      "Vendor points versus membership replication",
      "供应商点位与成分复制"
    ],
    "scope": [
      "Vendor series, available membership and proxy indices",
      "供应商序列、可得成分与代理指数"
    ],
    "status": [
      "Reference comparison",
      "参考对照"
    ],
    "finding": [
      "Published index points support return comparisons, while current membership snapshots lack historical effective dates and weights.",
      "已发布指数点位可以用于收益对照，但当前成分快照缺少历史生效日期和权重。"
    ],
    "boundary": [
      "Dividend conventions, pool differences and incomplete daily data prevent a certified index replication. A proxy index is a separate benchmark.",
      "分红口径、股票池差异和日频数据缺口使指数复制尚不能认证；代理指数属于另一基准。"
    ]
  },
  {
    "id": "H27",
    "title": [
      "Continuous-account execution diagnostic",
      "持续账户执行诊断"
    ],
    "scope": [
      "Public diagnostic dated 2026-09-28",
      "2026-09-28 公开诊断"
    ],
    "status": [
      "Short-sample mechanism check",
      "短样本机制检查"
    ],
    "finding": [
      "Continuous holdings and cash expose effects of participation, T+1, price limits and assumed fees. The public bilingual source is included in the appendices.",
      "持续持仓与现金揭示参与率、T+1、涨跌停和假设费用的影响；附录保留公开双语来源。"
    ],
    "boundary": [
      "This diagnostic does not certify full-history performance or actual capacity. A later method does not retroactively validate earlier ledgers.",
      "该诊断不能认证全历史业绩或真实容量；后来的方法也不能倒推证明早期账本有效。"
    ]
  },
  {
    "id": "H28",
    "title": [
      "Cross-market small-cap liquidity",
      "跨市场小盘流动性"
    ],
    "scope": [
      "A-share, Hong Kong, Japan and US; unmatched dates",
      "A 股、香港、日本和美国；日期未对齐"
    ],
    "status": [
      "Descriptive, quality-gated",
      "描述性证据，受质量门槛限制"
    ],
    "finding": [
      "Market-cap quantiles and USD ADV20 provide context, but dates, security types, units and eligibility differ. Some A-share totals do not reconcile.",
      "市值分位与美元 ADV20 提供背景，但日期、证券类型、单位与资格不同，部分 A 股总数无法核齐。"
    ],
    "boundary": [
      "Exclude inconsistent slices from rankings. Missing P90 cannot be replaced by a median; mean-versus-median lineage remains unresolved.",
      "口径不一致的切片应退出排名。不能用中位数代替缺失 P90，均值与中位数的数据沿袭仍待核实。"
    ]
  },
  {
    "id": "H29",
    "title": [
      "Order-book and impact calibration readiness",
      "盘口与冲击校准准备度"
    ],
    "scope": [
      "Ten-date book audit plus separate historical trades",
      "十个日期盘口审计及独立历史成交"
    ],
    "status": [
      "Partial coverage",
      "覆盖不完整"
    ],
    "finding": [
      "Published valid and excluded order-book counts reconcile, but missing minutes cluster on one date; a trades-only sample has no orders.",
      "公开盘口有效与剔除计数能够核齐，但缺失分钟集中在一天；另一段仅成交样本没有委托。"
    ],
    "boundary": [
      "Book counts are not actual-order capacity calibration. Require aligned orders, trades, timestamps and observed fills before estimating implementation cost.",
      "盘口计数不等于实际订单容量校准。估算执行成本前需对齐委托、成交、时间戳与实际成交记录。"
    ]
  },
  {
    "id": "H30",
    "title": [
      "Constrained full-history factor follow-up",
      "带约束的全历史因子复核"
    ],
    "scope": [
      "2008–2026 matched raw, constrained and net comparisons",
      "2008—2026 年原始、受约束与净收益匹配对照"
    ],
    "status": [
      "Promotion held",
      "暂缓晋级"
    ],
    "finding": [
      "Data checks passed, but only half of the core factor gates passed. Constraints and costs reduced apparent factor returns.",
      "数据检查通过，但核心因子门槛只通过一半；约束和成本削弱了表面收益。"
    ],
    "boundary": [
      "Theoretical shorts, terminal proxies and reconstructed point-in-time fundamentals remain limits. This does not rerun or validate every earlier long-only strategy.",
      "理论做空、终值代理与重建时点基本面仍是限制；这项研究没有重跑或证明所有早期纯多头策略。"
    ]
  },
  {
    "id": "H31",
    "title": [
      "Small-cap sensitivity artifact contract",
      "小盘敏感性制品约定"
    ],
    "scope": [
      "Adjacent factor-framework infrastructure",
      "相邻因子框架基础设施"
    ],
    "status": [
      "Infrastructure only",
      "仅基础设施"
    ],
    "finding": [
      "A small-cap sensitivity CSV is part of an output contract, with synthetic pipeline checks.",
      "输出约定包含小盘敏感性 CSV，并有合成数据流程检查。"
    ],
    "boundary": [
      "A file contract and synthetic test are not empirical small-cap evidence. No performance conclusion is added for this infrastructure.",
      "文件约定和合成测试不是实证小盘证据，这项基础设施不增加业绩结论。"
    ]
  },
  {
    "id": "H32",
    "title": [
      "Hong Kong provider, PIT and size-control probes",
      "港股供应商、时点基本面与规模控制探针"
    ],
    "scope": [
      "Archived monthly comparisons, March 2026",
      "2026 年 3 月归档月频对照"
    ],
    "status": [
      "Diagnostic, source-reported",
      "诊断性、来源报告"
    ],
    "finding": [
      "Provider and point-in-time fundamental portfolios differed substantially. The provider result accompanied small-cap and short-horizon price exposures; size-neutral and softer controls changed that exposure.",
      "供应商与时点基本面组合差异很大。供应商结果伴随小盘和短期价格敞口；规模中性与较温和控制改变了这些敞口。"
    ],
    "boundary": [
      "Style correlation does not establish causality. Better-controlled size exposure did not establish stronger structural alpha, and this Hong Kong sample cannot validate A-share micro-caps.",
      "风格相关不能证明因果。更受控的规模敞口没有确立更强的结构性超额收益，港股样本也不能证明 A 股微盘有效。"
    ]
  },
  {
    "id": "H33",
    "title": [
      "Four-stock micro-cap feasibility and cost stress",
      "四只微盘可行性与成本压力"
    ],
    "scope": [
      "September 2023–July 2026; 150 weekly formations",
      "2023 年 9 月至 2026 年 7 月；150 次周度形成"
    ],
    "status": [
      "Reconstructed proxy; substantial limits",
      "重建代理；限制明显"
    ],
    "finding": [
      "The strict historical-status window produced four selections at every formation. The standalone concentrated sleeve was highly sensitive to trading costs and experienced severe drawdowns; common-week index comparisons showed only partial agreement.",
      "严格历史状态窗口内每次形成均选出四只股票。这个高度集中子组合对交易成本十分敏感，回撤严重；共同周样本与指数只部分一致。"
    ],
    "boundary": [
      "This is a reconstructed proxy, with revision safety false, current master-data inputs and incomplete limit-price execution modeling. Historical ST coverage ends in July; do not extend the strict sample through August or call it index replication.",
      "这是重建代理，修订安全性为否，使用当前主数据，涨跌停执行建模不完整。历史 ST 覆盖止于 7 月，不能把严格样本延长至 8 月，也不能称为指数复制。"
    ]
  },
  {
    "id": "H34",
    "title": [
      "Cash-flow plus micro-cap allocation studies",
      "现金流加微盘配置研究"
    ],
    "scope": [
      "Three-year studies; broad proxy and separate four-stock sleeve",
      "三年研究；宽微盘代理与独立四只子组合"
    ],
    "status": [
      "Source-reported; share with caveats",
      "来源报告；附条件分享"
    ],
    "finding": [
      "The broad proxy comparison and later unified four-stock sleeve replay are distinct studies. A shared weekly calendar, next-session open execution and portfolio-level costs permitted a combined-account comparison.",
      "宽微盘代理对照与后续统一四只子组合重放是不同研究。共同周历、下一交易日开盘执行和组合层费用，使合并账户对照成为可能。"
    ],
    "boundary": [
      "The combined outcome does not isolate a micro-cap premium. Reconstructed fundamentals may contain later revisions; large drawdowns, concentration and incomplete execution constraints prevent live-capacity or formal point-in-time claims.",
      "混合结果不能单独识别微盘溢价。重建基本面可能包含后续修订；大回撤、集中度和不完整执行约束使其不能证明实盘容量或正式时点有效性。"
    ]
  },
  {
    "id": "H35",
    "title": [
      "Weekly size and beta neutrality feasibility",
      "周度规模与贝塔中性化可行性"
    ],
    "scope": [
      "Cached notebook comparisons: 2025 and partial 2026",
      "笔记本缓存对照：2025 年及部分 2026 年"
    ],
    "status": [
      "Cached exploratory evidence; not rerun",
      "缓存探索证据；未重跑"
    ],
    "finding": [
      "A concentrated candidate pool could not consistently satisfy portfolio size and beta constraints. Widening the candidate pool improved feasibility, while hard exposure controls reduced historical selected-sample excess returns.",
      "集中的候选池无法持续满足组合规模与贝塔约束。扩大候选池提高了可行性，但较硬的敞口控制也降低了历史选定样本的超额收益。"
    ],
    "boundary": [
      "The notebook reads existing comparison files and retains cached outputs; execution counters do not authenticate a fresh run. Samples were reused, lineage was incomplete and missing-outcome weights were flagged. Neither independent micro-cap alpha nor untouched out-of-sample performance is established.",
      "笔记本读取已有对照文件并保留缓存输出，执行计数不能认证新运行。样本已复用，来源链不完整，且标记了缺失收益权重问题；不能据此确立独立微盘超额收益或未查看的样本外业绩。"
    ]
  }
];

export const historyCopy = {
  "heading": [
    "Research history and coverage",
    "研究历史与覆盖"
  ],
  "intro": [
    "35 reviewed research families, including early explorations, corrections, blocked replays and protocols without verified results. These are editorial entries, not independent experiment counts.",
    "35 组已审查研究主题，覆盖早期探索、口径修正、受阻重放，以及尚无已核实结果的研究方案。这是编辑条目数，不是独立实验次数。"
  ],
  "scope": [
    "The report and Markdown share all entries and seven numerical table families (56 source rows). Restricted research appears only as reviewed high-level findings. Untracked notebooks and unavailable external runs are not certified complete.",
    "报告与 Markdown 共用全部条目及七组数值表（56 条来源记录）。受限研究仅展示经审查的概括性发现；未跟踪笔记本与不可得外部运行记录尚不能认定已全部覆盖。"
  ],
  "action": [
    "Read all evidence and numerical tables →",
    "阅读全部证据与数值表 →"
  ]
} as const;
