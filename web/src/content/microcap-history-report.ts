import { microcapHistory } from './microcap-history';
import type { ReportLocale } from './microcap-report.server';
type Row = Record<string, string | number>;
export type HistoricalSnapshot = Record<string, unknown> & { candidates: Row[]; anatomy: Row[]; capacity: Row[]; rebalance: Row[]; share_ledger: Row[]; joint_matrix: Row[] };
const origin = 'https://runchengxie.github.io/quant-market-research';
const table = (headers: string[], rows: string[][]) => [headers, headers.map(()=>'---'), ...rows].map(row=>`| ${row.map(v=>v.replaceAll('|','\\|')).join(' | ')} |`).join('\n');
export function historyMarkdown(locale: ReportLocale) {
  const zh=locale==='zh-CN'; const t=(en:string,cn:string)=>zh?cn:en;
  return [
    `## ${t('Research history and coverage register','研究历史与覆盖清单')}`,
    t('This is an editorial register of 34 reviewed research families, not 34 independent experiments. The review covers the known quantitative research repositories and selected adjacent infrastructure as of 2026-10-16. Language companions, migration copies and synthesis notes are deduplicated. It does not claim recovery of every untracked notebook, external runtime bundle or private trial.', '这里登记了 34 组已审查研究主题，不等于 34 项独立实验。范围是截至 2026-10-16 已核对的 quant 研究仓库及部分相邻基础设施；语言伴随文档、迁移副本和汇总笔记不重复计数。尚未证明所有未跟踪笔记本、外部运行结果包或私有试验都已恢复。'),
    t('The web report and downloadable Markdown use this same register. Restricted studies are represented only by reviewed high-level findings and limitations; private parameters, raw inputs and reproduction locations are excluded. Their source identities remain in the restricted provenance ledger. Public evidence links below support the public subset, not every restricted historical claim.', '网页报告与下载 Markdown 使用同一份清单。受限研究仅公开经审查的概括性发现与局限，不公开私有参数、原始输入或复现位置；来源身份保留在受限来源账册中。下方公开链接支持可公开的部分，不代表每项受限历史判断都有公开原文。'),
    ...microcapHistory.map(r=>`### ${r.id} · ${r.title[zh?1:0]}\n\n**${r.status[zh?1:0]} · ${r.scope[zh?1:0]}**\n\n${r.finding[zh?1:0]}\n\n${r.boundary[zh?1:0]}`),
    `### ${t('Public evidence anchors','公开证据入口')}`,
    `- [${t('Micro-cap history and method','微盘历史与方法')}](${origin}/docs/research/factors/microcap/${zh?'?lang=zh-CN':''})\n- [${t('Low-turnover history and corrections','低换手历史与修正')}](${origin}/docs/research/factors/low-turnover/${zh?'?lang=zh-CN':''})\n- [${t('Published numerical snapshot','已公开数值快照')}](${origin}/data/low_turnover_exploration.json)\n- [${t('Index reconstruction findings','指数重建发现')}](https://github.com/runchengxie/quant-market-research/blob/main/studies/index_replication/findings-20260909.md)\n- [${t('Liquidity evidence and quality gates','流动性证据与质量门槛')}](${origin}/research/liquidity/)`,
    t('Resumption requires source receipts for missing outputs, frozen future observations for selected rules, matched accounting for engine comparisons, and complete held-security valuation for returns. No research is promoted by this editorial consolidation.', '恢复研究需要补齐缺失输出的来源记录，为已选规则积累冻结后的新观察，统一不同引擎的核算，并补齐持仓证券计价。本次编辑整理不使任何研究自动晋级。'),
  ].join('\n\n');
}
export function historicalTablesMarkdown(snapshot: HistoricalSnapshot, locale: ReportLocale) {
 const zh=locale==='zh-CN'; const t=(en:string,cn:string)=>zh?cn:en;
 const n=(r:Row,k:string,d=2)=>Number(r[k]).toFixed(d);
 const p=(r:Row,k:string,fraction=false)=>`${(Number(r[k])*(fraction?100:1)).toFixed(2)}%`;
 const labels:Record<string,[string,string]>={small_cap:['Small cap','小盘'],low_turnover:['Low turnover','低换手'],low_turnover_residual:['Residual turnover','残差换手'],low_turnover_residual_industry:['Industry-residual turnover','行业残差换手'],composite:['Composite','复合'],composite_residual:['Residual composite','残差复合'],composite_residual_industry:['Industry-residual composite','行业残差复合'],large_cap_control:['Large-cap control','大盘对照'],lowvol_control:['Low-volatility control','低波动对照'],weekly:['Weekly','周频'],biweekly:['Biweekly','双周'],monthly:['Monthly','月频'],quarterly:['Quarterly','季频'],development:['Development','开发段'],holdout_descriptive:['Later descriptive','后段描述样本'],full_descriptive:['Full descriptive','全段描述样本'],raw:['Raw','原始'],size:['Size','规模'],size_lowvol:['Size + low volatility','规模与低波动'],size_lowvol_liquidity:['+ liquidity','再加流动性'],size_lowvol_liquidity_returns:['+ past returns','再加过去收益'],mean_20:['20-day mean','20 日均值'],mean_60:['60-day mean','60 日均值'],median_60:['60-day median','60 日中位数'],mean_120:['120-day mean','120 日均值']};
 const label=(v:string|number)=>labels[String(v)]?.[zh?1:0]??String(v);
 const fields=(en:string,cn:string)=>t(en,cn).split('|');
 const perfHeaders=fields('Annual net|Max drawdown|Sharpe|Annual turnover (×)','净年化|最大回撤|夏普|年换手（倍）');
 const perf=(r:Row)=>[p(r,'net_annual_return'),p(r,'net_max_drawdown'),n(r,'net_sharpe',3),n(r,'annualized_turnover')];
 return [
 `## ${t('Full published snapshot tables','公开快照完整表组')}`,
 t('The snapshot contains seven numerical families and 56 source rows: 9 candidates, 15 anatomy rows, 7 capital scenarios, 4 cadences, 2 ledgers, 16 joint cells and 3 windows. All rows are represented in this report; the three windows appear above. The JSON retains every machine field. Percentage return fields are already in percent; anatomy leg returns, fill ratios and cash weights are fractions and are converted for display. Rank IC and turnover multiples are not percentages.', '该快照包含七组数值、56 条来源记录：9 个候选、15 行分解、7 档资金、4 种频率、2 个账本、16 个联合单元和 3 个窗口。报告覆盖全部记录，三个窗口见前文；JSON 保留所有机器字段。收益百分数字段直接显示，分解中的多空腿收益、成交率和现金权重原为小数，展示时乘以 100；秩相关系数与换手倍数不是百分比。'),
 `### ${t('Nine candidates','九个候选')}`,
 `![${t('Nine historical candidates','九个历史候选')}](${origin}/downloads/microcap-candidates.${locale}.svg)`,
 table([t('Candidate','候选'),...perfHeaders,...fields('Blocked entry days|Blocked exit days','买入受阻天数|卖出受阻天数')],snapshot.candidates.map(r=>[label(r.candidate),...perf(r),String(r.blocked_entry_days),String(r.blocked_exit_days)])),
 `### ${t('Historical deconfounding anatomy','历史去混杂分解')}`,
 t('This earlier 133-formation panel is retained as history, not substituted for the later 86-month corrected common-support controls. Mean period returns are not annualized. The later inspected segment remains descriptive.', '此处保留较早的 133 次形成分解作为历史记录，不替代后续修正后的 86 个月共同样本控制。平均每期收益不是年化收益；后段已查看样本仍属描述性。'),
 table(fields('Sample|Control stage|Formations|Stock observations|Mean rank IC|Low-turnover leg|High-turnover leg|Low − high','样本|控制阶段|形成次数|股票观测数|平均秩相关|低换手腿|高换手腿|低减高'),snapshot.anatomy.map(r=>[label(r.sample),label(r.stage),String(r.formation_dates),String(r.observations),n(r,'mean_rank_ic',4),p(r,'low_turnover_leg_return',true),p(r,'high_turnover_leg_return',true),p(r,'low_minus_high_return',true)])),
 `### ${t('Seven capital scenarios','七档资金情景')}`,
 t('All use the composite candidate and assumed 5% participation. Rising simulated returns do not certify scalable capacity. Cash, delayed fills and uncalibrated impact can change the path.', '均为复合候选，假设参与率 5%。模拟收益随资金上升不能证明容量可扩展；现金、延迟成交和未校准冲击会改变路径。'),
 table(fields('Capital (CNY)|Annual net|Max drawdown|Sharpe|Fill ratio|Average cash|Delayed orders','资金（人民币元）|净年化|最大回撤|夏普|成交率|平均现金|延迟订单'),snapshot.capacity.map(r=>[String(r.capital),p(r,'net_annual_return'),p(r,'max_drawdown'),n(r,'net_sharpe',3),p(r,'fill_ratio',true),p(r,'avg_cash_weight',true),String(r.delayed_orders)])),
 `### ${t('Four rebalance cadences','四种调仓频率')}`,
 table([t('Cadence','频率'),...perfHeaders,...fields('Development annual|Later descriptive annual','开发段年化|后段描述年化')],snapshot.rebalance.map(r=>[label(r.rebalance_frequency),...perf(r),p(r,'development_annualized_return'),p(r,'holdout_annualized_return')])),
 `### ${t('Two continuous-share ledgers','两个持续份额账本')}`,
 t('These are comparison-only replays. Formations (139/296), weight targets (138/295) and owner replay periods (137/37) do not establish a matched sample. Cumulative-return machine fields have not been reinterpreted here. Modeled impact is zero; reported delay opportunity costs are uncalibrated and their currency basis needs confirmation.', '这两项是仅供比较的重放。形成次数（139/296）、权重目标次数（138/295）和所属引擎重放期数（137/37）尚不能证明样本匹配。此处不重新解释机器字段中的累计收益。模拟冲击为零；所报延迟机会成本未经校准，币种口径仍需确认。'),
 table(fields('Cadence|Formations|Annual net|Max drawdown|Sharpe|Fill ratio|Average cash|Cumulative turnover (×)|Delayed orders|Reported delay cost','频率|形成次数|净年化|最大回撤|夏普|成交率|平均现金|累计换手（倍）|延迟订单|所报延迟成本'),snapshot.share_ledger.map(r=>[label(r.rebalance_frequency),String(r.formation_dates),p(r,'share_ledger_net_annual_return'),p(r,'share_ledger_max_drawdown'),n(r,'share_ledger_net_sharpe',3),p(r,'share_ledger_fill_ratio',true),p(r,'share_ledger_avg_cash_weight',true),n(r,'share_ledger_cumulative_turnover'),String(r.share_ledger_delayed_orders),n(r,'share_ledger_delay_opportunity_cost')])),
 `### ${t('All 16 definition × cadence records','全部 16 条定义 × 频率记录')}`,
 table([...fields('Definition|Cadence|Formations','定义|频率|形成次数'),...perfHeaders,...fields('Development annual|Later descriptive annual','开发段年化|后段描述年化')],snapshot.joint_matrix.map(r=>[label(r.turnover_definition),label(r.rebalance_frequency),String(r.formation_dates),...perf(r),p(r,'development_annualized_return'),p(r,'holdout_annualized_return')])),
 t('Version warning: candidate, cadence and ledger numbers differ from earlier narrative reports. Apart from explicitly documented corrections, this compilation does not attribute every difference to a single cause. The snapshot also retains a stale caveat saying the joint grid is pending despite containing 16 cells. These conflicts remain visible rather than being silently reconciled.', '版本提示：候选、调仓与账本数字与早期叙述报告存在差异。除明确记载的修正外，本汇编不把所有差异归结为同一原因。快照还保留了“联合矩阵待生成”的旧提示，尽管已有 16 个单元。这些冲突继续公开保留，不作无依据的合并解释。'),
 ].join('\n\n');
}
