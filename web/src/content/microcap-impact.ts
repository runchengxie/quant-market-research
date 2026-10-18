import data from '../../public/data/microcap_impact_review.json';
import type { LocalText } from './microcap-hub';
import { tAgenda, type AgendaLocale } from './microcap-agenda';
export const impactEvidence=data;
export const impactCopy={
 title:['Which unresolved events touch holdings?','哪些未解决事件真正碰到了持仓？'],
 intro:['Across the same union of 94 dated blocker groups, seven intersect at least one retained minimum-90 simulated inventory. Six other groups have record dates outside the retained fill-account window and remain unknown. One row without an ex-date remains separate. These counts prioritize source review; they do not clear action blockers.','在同一组 94 个已知日期阻塞事件中，7 个与至少一种保留的 90 观测方案模拟持仓相交；另有 6 个的登记日不在保留成交账本区间内，仍属未知。另有一行除权日未知，单独保留。这些计数用于安排补证优先级，没有解除事件阻塞。'],
 exposureTitle:['Targets, fills and unknown coverage','目标持仓、成交库存与未知覆盖'],
 exposureBoundary:['Minimum 45 / 90 means the minimum valid observations in the historical 120-session turnover window; it is separate from the future 60-session study. Each row independently partitions all 94 dated groups, rather than the separate owner totals of 83 / 82. Target membership uses the preceding formation; inventory uses record-date end-of-day fills. Minimum-45 fills were not retained, so its inventory is unavailable. The four minimum-90 ledgers cover June 1, 2015 through July 31, 2026. Synthetic adjusted units do not establish raw shares or holder entitlements.','45／90 指历史 120 个交易日换手窗口所需的最低有效观测数，与未来 60 日研究不同。每行各自划分全部 94 个已知日期事件，不是两套方案各自的 83／82 个阻塞数。目标持仓取登记日前的形成记录，库存取登记日收盘后的成交余额。45 观测方案没有保留成交账本，其库存仍未知；四种 90 观测账本覆盖 2015-06-01 至 2026-07-31。复权合成份额不能直接确定真实股份或持有人权益。'],
 stressTitle:['Conditional one-event stress, without a global loss bound','单个事件的条件冲击，尚无全局损失边界'],
 stress:['The observed exposed positions represent roughly 1.52–2.62% of same-date simulated NAV in the ideal account and 2.11–2.63% under the prior-20/realized-volume guard. If exactly one such marked position is reduced by an assumed 10%, with everything else unchanged, the mechanical NAV reduction is shown below. The 10% haircut is an explicit assumption, not an estimated event loss.','已观察到的涉事持仓，在理想账本中约占当日模拟净值的 1.52%—2.62%，在滞后量与当日量约束账本中约占 2.11%—2.63%。假设只把其中一笔持仓的标记市值下调 10%，其余保持不变，下表给出净值的机械变化。10% 是明确的情景假设，不是估计出的事件损失。'],
 stressBoundary:['These are different event dates and cannot be added. They are neither empirical confidence intervals nor worst-case bounds for all missing actions. Missing raw-share inventory, action terms, settlement and tax prevent identification of a corrected full-period account NAV range.','这些观察来自不同事件日期，不能相加。它们不是经验置信区间，也不是全部缺失事件的最坏损失上界。真实股份库存、事件条款、结算与税费尚未齐全，因此还不能确定完整区间账户净值的修正范围。'],
 accountTitle:['A sourced raw-price account chain','由真实来源支持的原始价格账户核对'],
 account:['Four constructed accounts use real raw-price windows and an assumed CNY 100,000 cash start, 90% purchase target, 100-share lots, T+1 and a flat 10 bp fee. They cover capitalization shares, gross cash distributions, an exposure-prioritized event and a conditionally blocked exit. Source terms and quotes independently determine record inventory, rights, settlement, marks and fee checks. Coherently wrong rights, marks and fees are rejected by regression tests.','四个构造账户使用真实原始价格区间，假设初始现金 10 万元、90% 买入目标、100 股交易单位、T+1 和统一 10bp 费用，覆盖转增股份、税前现金分配、暴露清单优先事件及受约束退出。核对依据是来源条款和报价，独立计算登记日库存、权益、结算、计价与费用；整套输出一同偏离条款、价格或费用时，回归测试也会拒绝。'],
 accountBoundary:['These are mechanism accounts, not selected-portfolio or broker accounts. One additional exposed event has primary-reviewed economic terms, while owner blockers remain 83 / 82 and selected-portfolio entitlements are uncertified. One provider suspension flag conflicts with a primary resumption announcement: that exit is a conservative conditional scenario, not proof of absolute intraday nontradability. No real multi-day settlement delay is observed here; delayed rights are covered by synthetic tests.','这些是机制验证账户，不是所选策略或券商账户。本轮另核实了一个涉持仓事件的公告经济条款，原解析器阻塞仍为 83／82，策略账户权益尚未认证。一项供应商停牌标记与公告复牌安排冲突，对应退出只作为保守约束情景，不据此认定当日绝对无法成交。本轮真实案例没有覆盖跨日延迟结算，延迟权益由合成测试检验。'],
 registerTitle:['Continuous records that retain earlier failures','保留先前失败状态的连续登记'],
 register:['A local register now imports the original two pending receipts in order: eight issues followed by seven. Original receipt times and the later import times remain separate. Subsequent manual reviews select the recorded predecessor automatically and bind inputs, code, lock file and available signal evidence. These imports are not new market observations: admitted and completed counts remain zero, and no scheduler is installed.','本地登记册已按顺序导入原有两份待定记录：先有八类问题，后有七类。原收据时间与后来的导入时间分开保留。后续人工复查自动取已登记的前一份记录，并绑定输入、代码、依赖锁和已有信号证据。两次导入不是新的市场观察，纳入和完成数量仍为零，也没有安装定时任务。'],
 registerBoundary:['The published head below anchors this two-entry prefix. Compare it with the reviewed version before continuing. Local hashes and witnesses do not independently prevent replacement of the entire directory; later unanchored entries need new independent anchors. Integrity checks do not prove historical availability or validate signal ranks.','下方公布的末项哈希锚定这两条记录。继续登记前，应与已审查版本对照。本地哈希和见证文件不能单独防止整个目录被替换，后续尚未锚定的记录需要新的独立锚点。完整性检查不证明历史信息可得性，也不验证信号排名。'],
 provenance:['Reviewed aggregate provenance','已审查汇总的来源记录'],
 download:['Download reviewed exposure and account aggregates','下载已审查的持仓交集与账户汇总'],
} satisfies Record<string,LocalText>;
const label=(en:string,zh:string,l:AgendaLocale)=>l==='zh-CN'?zh:en;
const fmt=(v:number,l:AgendaLocale,d=2)=>new Intl.NumberFormat(l,{minimumFractionDigits:d,maximumFractionDigits:d}).format(v);
const armLabels:Record<string,LocalText>={
 owner_ideal_fee10:['90-observation · ideal fills','90 观测 · 理想成交'],
 capacity_without_limits:['90-observation · capacity, no limit gate','90 观测 · 容量约束，不加涨跌停限制'],
 capacity_with_limits:['90-observation · capacity and limit gates','90 观测 · 容量与涨跌停约束'],
 prior20_budget_realized_guard:['90-observation · prior-20 and realized-volume guard','90 观测 · 滞后量与当日量约束'],
};
export function impactTable(l:AgendaLocale){const parts=['definite','possible','absent','unknown'] as const;return {
 headers:label('Plan / observation|Positive exposure|Possible|Absent|Unknown','方案／观察|明确持仓|可能持仓|未持仓|未知',l).split('|'),
 rows:[...(['45','90'] as const).map(p=>[label(`${p}-observation · preceding target`,`${p} 观测 · 前次目标持仓`,l),...parts.map(k=>String(data.exposure.plans[p].target[k]))]),
 ...Object.entries(data.exposure.plans['90'].inventory).map(([arm,row])=>[tAgenda(armLabels[arm],l),...parts.map(k=>String(row[k]))])],
};}
export function stressTable(l:AgendaLocale){return {
 headers:label('Account|Marked position, CNY million|Position / same-date NAV %|Assumed 10% haircut: NAV reduction %','账户|持仓标记市值，百万元|持仓／当日净值 %|假设下调 10%：净值减少 %',l).split('|'),
 rows:Object.entries(data.exposure.materiality).map(([arm,r])=>[tAgenda(armLabels[arm],l),`${fmt(r.position_value_cny_min/1e6,l)}–${fmt(r.position_value_cny_max/1e6,l)}`,`${fmt(r.position_fraction_nav_min*100,l)}–${fmt(r.position_fraction_nav_max*100,l)}`,`${fmt(r.conditional_nav_loss_fraction_min*100,l)}–${fmt(r.conditional_nav_loss_fraction_max*100,l)}`]),
};}
const caseLabels:Record<string,LocalText>={
 'account-1':['Capitalization control','转增股份对照'], 'account-2':['Gross cash control','税前现金分配对照'],
 'account-3':['Exposure-prioritized case','暴露清单优先案例'], 'account-4':['Conditional blocked exit','条件约束下的受阻退出'],
};
export function accountTable(l:AgendaLocale){return {headers:label('Constructed account|Sessions|Fills|Largest accounting discrepancy, CNY','构造账户|交易日|成交笔数|最大核算差异，元',l).split('|'),rows:data.account.cases.map(r=>[tAgenda(caseLabels[r.case_id],l),String(r.sessions),String(r.fills),r.max_identity_error.toExponential(2)])};}
export function registerTable(l:AgendaLocale){return {headers:label('Sequence|Original receipt as-of UTC|Imported UTC|Pending categories','顺序|原收据截至时间 UTC|导入时间 UTC|待补类别',l).split('|'),rows:data.register.observations.map(r=>[String(r.sequence),r.original_as_of_utc,r.imported_utc,String(r.issue_count)])};}
const md=(table:{headers:string[];rows:string[][]})=>[table.headers,table.headers.map(()=>'---'),...table.rows].map(row=>`| ${row.map(s=>s.replaceAll('|','\\|')).join(' | ')} |`).join('\n');
export function impactMarkdown(l:AgendaLocale){const t=(key:keyof typeof impactCopy)=>tAgenda(impactCopy[key],l);return [
 `## ${t('title')}`,t('intro'),`### ${t('exposureTitle')}`,md(impactTable(l)),t('exposureBoundary'),
 `### ${t('stressTitle')}`,t('stress'),md(stressTable(l)),t('stressBoundary'),
 `### ${t('accountTitle')}`,t('account'),md(accountTable(l)),t('accountBoundary'),
 `### ${t('registerTitle')}`,t('register'),md(registerTable(l)),t('registerBoundary'),`SHA-256: \`${data.register.head_sha256}\``,
 `### ${t('provenance')}`,`[${t('download')}](https://runchengxie.github.io/quant-market-research/data/microcap_impact_review.json)`,
 ...Object.entries(data.source_sha256).map(([role,hash])=>`- ${role}: \`${hash}\``),
].join('\n\n');}
