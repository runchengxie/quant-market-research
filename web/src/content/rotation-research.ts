// Public projection: reviewed aggregate observations and explanatory copy only.
// No strategy parameters, holdings, raw inputs, or private reproduction locators.
export type Copy = readonly [string, string];
export type Group = 'risk' | 'pool' | 'holdover' | 'score';
export type WeeklyRow = { id: string; group: Group; label: Copy; cagr: number; sharpe: number; drawdown: number; fallback: number | null; executions: number | null };
export const groupLabels: Record<Group, Copy> = {
  risk: ['Risk exposure and allocation', '风险仓位与组合配置'],
  pool: ['ETF universe expansion', 'ETF 候选池扩展'],
  holdover: ['Holding continuity', '持仓延续'],
  score: ['Scoring model', '评分模型'],
};
const row = (id: string, group: Group, label: Copy, cagr: number, sharpe: number, drawdown: number, fallback: number | null = null, executions: number | null = null): WeeklyRow => ({ id, group, label, cagr, sharpe, drawdown, fallback, executions });
export const weeklyRows: WeeklyRow[] = [
  row('fixed-base', 'risk', ['Fixed slots · baseline', '固定仓位 · 基准'], 6.37, .480, -22.86, 31.44),
  row('fixed-75', 'risk', ['Fixed slots · 75% risk cap', '固定仓位 · 风险上限 75%'], 6.23, .549, -18.09, 42.71),
  row('fixed-50', 'risk', ['Fixed slots · 50% risk cap', '固定仓位 · 风险上限 50%'], 5.86, .705, -11.61, 57.25),
  row('hrp-base', 'risk', ['HRP allocation · baseline', '层次风险平价 · 基准'], 8.65, .709, -20.21, 38.88),
  row('hrp-75', 'risk', ['HRP allocation · 75% risk cap', '层次风险平价 · 风险上限 75%'], 6.70, 1.026, -8.56, 64.22),
  row('hrp-50', 'risk', ['HRP allocation · 50% risk cap', '层次风险平价 · 风险上限 50%'], 6.69, 1.034, -8.56, 64.87),
  row('qp-base', 'risk', ['Minimum variance · baseline', '最小方差 · 基准'], 8.35, .678, -20.09, 31.81),
  row('qp-75', 'risk', ['Minimum variance · 75% risk cap', '最小方差 · 风险上限 75%'], 6.31, .883, -8.58, 54.96),
  row('qp-50', 'risk', ['Minimum variance · 50% risk cap', '最小方差 · 风险上限 50%'], 6.16, .945, -8.45, 60.87),
  row('pool-core', 'pool', ['Core · HRP', '核心池 · 层次风险平价'], 6.70, 1.026, -8.56),
  row('pool-cash', 'pool', ['Core + cash-flow style', '核心池＋现金流风格'], 6.70, 1.026, -8.56),
  row('pool-1000', 'pool', ['Core + CSI 1000 style', '核心池＋中证 1000 风格'], 6.81, 1.041, -8.53),
  row('pool-2000', 'pool', ['Core + CSI 2000 style', '核心池＋中证 2000 风格'], 6.86, 1.048, -8.56),
  row('pool-quality', 'pool', ['Core + quality style', '核心池＋质量风格'], 6.33, .979, -8.56),
  row('pool-dividend', 'pool', ['Core + dividend low volatility', '核心池＋红利低波'], 6.40, .982, -8.56),
  row('pool-both', 'pool', ['Core + quality + dividend', '核心池＋质量＋红利低波'], 6.05, .936, -8.56),
  row('pool-pruned', 'pool', ['Dynamic correlation pruning · HRP', '逐期相关性去重 · 层次风险平价'], 6.21, 1.122, -7.31),
  row('hold-base', 'holdover', ['Fixed slots · baseline', '固定仓位 · 基准'], 6.37, .480, -22.86, null, 649),
  row('hold-mild', 'holdover', ['Moderate holding continuity', '适度持仓延续'], 6.00, .461, -22.86, null, 595),
  row('hold-wide', 'holdover', ['Broader holding continuity', '更宽的持仓延续'], 5.17, .441, -22.86, null, 551),
  row('score-base', 'score', ['Frozen score · fixed slots', '固定评分 · 固定仓位'], 6.37, .480, -22.86, null, 649),
  row('score-low', 'score', ['Ridge challenger A · fixed slots', '岭回归方案 A · 固定仓位'], 5.70, .455, -20.96, null, 690),
  row('score-mid', 'score', ['Ridge challenger B · fixed slots', '岭回归方案 B · 固定仓位'], 5.74, .449, -20.96, null, 676),
  row('score-high', 'score', ['Ridge challenger C · fixed slots', '岭回归方案 C · 固定仓位'], 6.24, .473, -22.86, null, 680),
];
export function selectWeeklyRows(group: Group) { return weeklyRows.filter(value => value.group === group); }
export const groupNotes: Record<Group, Copy> = {
  risk: ['Compare each allocator with its own uncapped baseline. Lower drawdowns came with lower annualized returns and larger bond allocations. The bond fallback carries duration risk; it is not cash. HRP groups correlated exposures before balancing risk; minimum variance minimizes estimated portfolio variance without forecasting returns.', '每种配置方法应与自身无仓位上限的基准比较。回撤降低的同时，年化收益下降、债券配置增加。防守端仍承担债券久期风险，不能当作现金。层次风险平价先按相关性分组再分配风险；最小方差依据估计协方差配置，不负责预测收益。'],
  pool: ['All rows here use the defensive HRP path and a 75% total risk cap. Small-cap additions improved this historical sample only modestly; quality and dividend additions did not improve it. Dynamic correlation pruning reduced drawdown but also reduced annualized return. Cash-flow exposure arrived too late to affect most of the sample.', '本组均使用防守型层次风险平价配置和 75% 风险仓位上限。加入小盘风格只带来小幅历史改善，质量与红利低波未带来改善。逐期相关性去重降低了回撤，也降低了年化收益。现金流 ETF 的有效历史较短，对样本大部分区间没有影响。'],
  holdover: ['Only the fixed-slot holding-continuity rule changes. Executed rebalances fall from 649 to 595 or 551, but annualized returns also fall and maximum drawdown does not improve. Fewer trades alone do not establish a better strategy.', '只改变固定仓位组合的持仓延续规则。执行调仓次数从 649 次降到 595 或 551 次，但年化收益也下降，最大回撤没有改善。交易更少本身不能证明策略更好。'],
  score: ['These rows hold the fixed-slot construction and execution protocol constant. Three prior-constrained Ridge challengers did not exceed the frozen score’s annualized return or Sharpe ratio. They are historical challenges, not independent holdout tests. A/B/C identify distinct retained runs without publishing private fitting settings.', '这些行保持固定仓位构造和执行口径一致。三组带先验约束的岭回归方案都没有超过固定评分的年化收益或夏普比率。它们是历史对照，不是独立留出检验。A、B、C 区分保留的实验，不公开私有拟合参数。'],
};
export const researchSteps: { title: Copy; text: Copy; gap: Copy }[] = [
  { title: ['Observe style and theme signals', '识别风格与主题信号'], text: ['Style exposures describe differences such as size, value or quality. Theme heat describes attention to an industry or narrative. A strong signal is a hypothesis about future returns, not a realized return.', '风格暴露描述规模、价值或质量等差异；主题热度描述行业或叙事受到的关注。信号强只是对未来收益的假设，并不等于已经获得收益。'], gap: ['Need: evidence of when each signal became available.', '待补：每项信号在当时何时可得的凭证。'] },
  { title: ['Map signals to investable ETFs', '映射到可交易 ETF'], text: ['A theme label must be connected to an ETF’s actual exposure, listing history, liquidity and overlapping holdings. Multiple ETFs tracking similar assets do not create independent opportunities.', '主题标签需要对应 ETF 的真实暴露、上市历史、流动性和持仓重叠。多只 ETF 跟踪相近资产，并不代表获得了多个独立机会。'], gap: ['Need: dated mapping, historical eligibility and tracking-error checks.', '待补：带日期的映射、历史准入资格和跟踪误差核验。'] },
  { title: ['Rank exposures and build a portfolio', '排序暴露并构造组合'], text: ['Separate which exposures to own from how much to allocate. Ranking, risk limits, correlation control and holding continuity answer different questions and need separate matched baselines.', '把选择哪些暴露与分配多少仓位分开。排序、风险上限、相关性控制和持仓延续回答不同问题，都需要口径一致的独立对照。'], gap: ['Observed: several historical configuration challenges; forward confirmation pending.', '已有：多组历史配置对照；尚待前瞻验证。'] },
  { title: ['Account for execution and test forward', '计入执行约束并前瞻验证'], text: ['Translate target weights into feasible trades, account for costs and unavailable prices, freeze the comparison, then observe genuinely new dates. Re-examining old dates cannot create a new out-of-sample record.', '把目标权重转成可执行交易，计入成本与缺失价格，冻结比较方案，再观察真正的新日期。反复检视旧区间，不能产生新的样本外记录。'], gap: ['Need: a continuous execution ledger and a frozen forward comparison.', '待补：连续执行账本与预先冻结的前瞻对照。'] },
];
export const experimentCards: { family: 'etf' | 'hotspot' | 'bridge'; title: Copy; observation: Copy; scope: Copy; next: Copy; anchor: string }[] = [
  { family: 'etf', title: ['Legacy ETF ranking models', '旧版 ETF 排序模型'], observation: ['All three recipes trail the fixed basket at 25 bps; a small zero-cost raw-price advantage is not robust to adjusted valuation.', '三种模型在 25 基点成本下都落后于固定篮子；零成本、原始价格下的小幅优势在复权口径下不稳健。'], scope: ['1,183 matched open-to-open periods · 2021–2025 · conditional historical tail', '1,183 个匹配开盘区间 · 2021—2025 · 条件历史尾段'], next: ['Freeze a new sample, availability evidence and a consistent cost ledger.', '冻结新样本、输入可得性凭证和一致的成本账本。'], anchor: 'etf-rotation' },
  { family: 'etf', title: ['Weekly ETF risk allocation', '周频 ETF 风险配置'], observation: ['Risk caps trade some annualized return for shallower historical drawdowns; larger bond exposure explains part of the change.', '风险上限牺牲部分年化收益，换来较浅的历史回撤；债券占比上升是变化的一部分。'], scope: ['Panel: 2015-01-05–2026-08-24 · 5 bps execution assumption · historical reuse', '行情面板：2015-01-05 至 2026-08-24 · 假设成本 5 基点 · 历史重复检视'], next: ['Test the return–drawdown trade-off on a frozen forward period.', '在冻结的前瞻区间检验收益与回撤的取舍。'], anchor: 'weekly' },
  { family: 'etf', title: ['Universe, continuity and score challengers', '候选池、持仓延续与评分对照'], observation: ['Broad industry expansion did not improve the recorded strategy. Smaller style additions were mixed; holding continuity and Ridge did not establish superiority.', '广泛扩展行业池未改善该次策略结果。少量风格扩池结果不一；持仓延续与岭回归没有证明优于基准。'], scope: ['Related historical runs · separate baselines · not additional independent samples', '相关历史实验 · 各自基准 · 不构成新增独立样本'], next: ['Separate diversification effects from extra parameter search.', '区分分散化效果与增加参数搜索带来的表面改善。'], anchor: 'weekly' },
  { family: 'hotspot', title: ['Hotspot stock overlay', '热点个股叠加筛选'], observation: ['Three of four isolated events favor the overlay; this is a stock-candidate experiment, not an ETF portfolio test.', '四个独立事件有三个因叠加筛选而改善；这是个股候选实验，不是 ETF 组合验证。'], scope: ['Four five-session events in 2025 · aggregate-only · no continuous NAV', '2025 年四个五日事件 · 仅汇总统计 · 无连续净值'], next: ['New dates, contemporaneous input receipts and a continuous paired portfolio.', '补充新日期、当时输入凭证和连续配对组合。'], anchor: 'hotsector' },
  { family: 'bridge', title: ['Theme-to-ETF transmission', '主题到 ETF 的传导验证'], observation: ['The shared research question is clear; the existing hotspot events do not establish that mapping attention into ETFs adds value.', '共同研究问题已经清楚；现有热点事件仍不能证明把关注度映射成 ETF 仓位能增加收益。'], scope: ['Proposed research bridge · no published performance result', '拟研究的衔接环节 · 尚无公开业绩结果'], next: ['Compare the same ETF universe with and without frozen theme information.', '在相同 ETF 池上，只改变是否使用已冻结的主题信息。'], anchor: 'next-tests' },
];
export const rotationCopy = {
  title: ['Style and theme rotation: from signals to ETF portfolios', '风格与主题轮动：从信号到 ETF 组合'],
  intro: ['Can changing style and theme exposures produce a tradable ETF allocation advantage? This topic brings related research together while keeping each strategy identity, baseline and evidence boundary distinct.', '风格与主题的变化，能否转化为可交易的 ETF 配置优势？本专题把相关探索放在同一条研究主线上，同时保留各策略的身份、比较基准和证据边界。'],
  conclusion: ['The evidence supports further testing, not a claim of a reliable edge. Legacy ETF models struggle after costs; weekly allocation experiments expose return–risk trade-offs; hotspot evidence is small and stock-based. The complete theme-to-ETF chain remains unvalidated.', '现有证据支持继续研究，尚不足以宣称存在稳定优势。旧版 ETF 模型在成本后表现不足；周频配置实验揭示收益与风险的取舍；热点证据样本很小，而且来自个股。完整的“主题信号—ETF 映射—组合收益”链路仍待验证。'],
  weeklyProtocol: ['These aggregate results were transcribed and checked against retained research notes, not rerun for this page. The source panel covers 2015-01-05 through 2026-08-24; that is input coverage, not a verified common performance start date. Runs use actual observed ETF history, next-observed-session close execution, and a 5 bp gross-traded-notional cost assumption. Cost scenarios are not brokerage quotes. The first usable return date is not independently established here. Separate groups retain their original comparisons.', '这些汇总结果已对照保留的研究记录逐项核对，本页面没有重新回测。来源行情面板覆盖 2015-01-05 至 2026-08-24；这是输入覆盖期，不是已核验的共同业绩起点。实验使用 ETF 实际观测历史，按下一可观测交易日收盘执行，假设按交易总额收取 5 基点成本。成本是假设情景，不是券商报价。这里未独立确认各实验首个有效收益日期。不同组保留各自原有对照。'],
  weeklyLimits: ['Historical diagnostics from a repeatedly examined sample. Metrics are rounded source-note aggregates; no raw daily ledger or continuous equity curve is published. Sharpe uses a zero-rate convention where specified by the pool study; a uniform recomputation across all runs is pending. Do not compare these annualized returns with the legacy chart’s cumulative return or with hotspot event uplift. None of these results authorizes live trading.', '这些是反复检视过的历史样本诊断。数值为研究记录中的取整汇总，未公开逐日账本或连续净值。候选池研究注明使用零利率夏普口径；所有实验的统一重算仍待完成。不能把这里的年化收益与旧版模型的累计收益、热点事件的增量直接排名。这些结果都不构成实盘资格。'],
} satisfies Record<string, Copy>;
