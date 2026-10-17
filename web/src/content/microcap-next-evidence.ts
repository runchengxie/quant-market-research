import data from '../../public/data/microcap_next_evidence_review.json';
import { tAgenda, type AgendaLocale } from './microcap-agenda';
import type { LocalText } from './microcap-hub';
export const nextEvidence = data;
export const nextCopy = {
 outcomesTitle:['Four real notices, assumed inventory and accounting outcomes','四份真实公告、假设持仓与核算结果'],
 outcomesBoundary:['Each example starts with 1,000 unrestricted original shares, zero cash and no trades. P is an unobserved symbolic share price; P=1 is only a unit valuation. The table holds that unit mark fixed and omits market repricing and taxes, so changes in unit NAV are not investment gains or returns. Payment/listing dates are issuer-scheduled dates, not observed account receipts or proof that shares can be sold.', '各例均假设原股东持有 1,000 股非限售股，期初现金为零，没有交易。P 是未观察到的符号股价，P=1 只用于单位计价。表中固定这个单位价格，未计市场重新定价与税费，因此单位净值的变化不能当作投资盈利或收益率。派息、上市日期按发行人安排记录，不能据此确认账户实际到账或股份可卖。'],
 sourcesTitle:['Independent public notices used for the examples','案例使用的独立公开公告'],
 sourcesBoundary:['These issuer notices illustrate accounting terms independently; linking them does not identify membership in either frozen target plan. The notices are in Chinese.', '这些发行人公告独立说明核算条款；列出链接不代表披露任一冻结目标方案的成分。公告原文为中文。'],
 eventTitle:['Event evidence improves; account readiness does not change','事件证据有进展，账户仍未就绪'],
 eventDetails:['Blocker priorities and accounting lessons','阻塞优先级与核算教训'],
 eventBoundary:['The three reviews settle economic interpretation retrospectively; they do not release the owner resolver. One reviewed cash case still has unresolved period metadata, and another requires holder classification. Primary-source coverage is incomplete, and missing or conflicting amounts cannot be filled with zero. A globally latest source row cannot safely replace holder-specific and event-specific adjudication.', '三项复查回顾性地明确了经济含义，但没有解除原有事件解析器的阻塞。其中一个现金案例的期间元数据仍未解决，另一个还需确认持有人类别。原始公告核验还不完整，缺失或冲突的金额不能补零；也不能拿全局最新一行替代逐事件、按持有人资格的裁定。'],
 caseBoundary:['Examples use assumed gross holdings and a unit valuation mark, without trades. Executable sellable shares remain unknown. They test accounting mechanics only and do not reconstruct strategy holdings, actual payments or portfolio NAV. Historical availability at formation is a separate requirement.', '案例使用假设的税前持股权益与单位计价，没有交易，只检验核算机制；实际可执行的可卖股数仍未知。它们没有重建策略持仓、实际到账或组合净值；形成时点的信息可得性还须另行核验。'],
 title:['Latest evidence review · October 18, 2026','最新证据复查 · 2026 年 10 月 18 日'],
 readinessTitle:['Future input readiness remains pending','前瞻输入仍待准备'],
 readiness:['The October 30 candidate has not been admitted. The updated readiness check records seven pending categories, and the new cohort still has zero completed months. The official published calendar schedule has been cross-checked; six source roles and the signal still await future formation inputs. These are preparation gaps before the cutoff, not failed return observations.', '10 月 30 日候选尚未纳入前瞻样本。更新后的就绪检查记录了七类待补材料，新样本已完成月份仍为零。官方公布的交易日安排已交叉核对，六类来源和信号仍要等未来形成时点的输入。这些是截止时点前的准备缺口，不是收益观察失败。'],
 provenance:['The initial receipt at 2026-10-17 23:39:31 UTC retained eight pending categories. A continuation at 23:48:39 UTC closes only official-calendar verification and retains seven; the earlier receipt is preserved. The legacy manifest and August archive hashes still match the frozen record. Matching bytes and declared timestamps do not prove when information was historically available. Even a structurally complete package still needs independent provenance and signal-content audits before admission.', '2026-10-17 23:39:31 UTC 的首份收据保留了八类待补材料；23:48:39 UTC 的后续收据仅关闭官方日历核验这一项，余下七类，首份收据继续留存。旧版清单和八月归档的哈希仍与冻结记录一致。文件一致和声明时间不能证明信息在历史上何时可得。即使材料结构齐全，纳入样本前仍要独立核验来源和信号内容。'],
 calendarTitle:['Official schedule cross-check','官方交易日安排交叉核对'],
 calendar:['Two retained SSE notices support the published October/November schedule. Across 61 civil days, 17 October and 21 November sessions match the vendor calendar with zero mismatches. The schedule places formation on October 30, entry on November 2 and the holding endpoint on November 30. Recheck amendments and emergency closures before the actual freeze; these are scheduled dates, not observed future sessions or admitted signals.', '保留的两份上交所公告支持十月、十一月的公开交易日安排。61 个自然日中，十月 17 个、十一月 21 个交易日与供应商日历一致，差异为零。按当前安排，形成日为 10 月 30 日，入场日为 11 月 2 日，持有期终点为 11 月 30 日。实际冻结前还须复查修订和临时休市；这些是计划日期，不是已观察到的未来交易日，也不代表信号已纳入样本。'],
 readinessDetails:['Pending inputs and admission boundary','待补输入与样本纳入边界'],
 gateTitle:['What must happen before capacity tests resume?','容量检验恢复前还缺什么？'],
 gate:['Primary-event adjudication, inventory entitlement and settlement, and raw-price valuation must reconcile before capital/cost break-even reruns. Calibrated market impact additionally requires actual spread, depth and fill observations. No new capital grid or capacity estimate was run in this review; full-window raw-share readiness remains false and the original 120-session runtime remains unrecovered.', '重跑资金与成本盈亏平衡检验前，须先完成原始事件裁定，核对持仓权益与结算，并用原始价格对齐计价。校准市场冲击还需要实际价差、盘口深度和成交记录。本次复查没有重跑资金网格，也没有新增容量估计；全区间真实股份账户仍未就绪，120 日历史原始运行仍未找回。'],
 download:['Download reviewed follow-up aggregates','下载已审查的后续汇总'],
 boundary:['Only reviewed aggregates and case mechanics are public. Source rows, security identifiers, holdings and private reproduction paths remain outside this site.', '这里只公开已审查的汇总与案例核算方法。来源明细、证券代码、持仓及私有复现路径不进入网站。'],
} satisfies Record<string,LocalText>;
const issues:Record<string,LocalText>={
 benchmark:['Benchmark','基准'],calendar:['Independent official calendar verification','独立核验官方交易日历'],capitalization_valuation:['Capitalization and valuation','市值与估值'],industry_membership:['Industry membership','行业归属'],prices_adjustments:['Prices and adjustments','价格与复权'],signal:['Frozen signal','冻结信号'],turnover_amounts:['Turnover and amounts','换手与成交额'],universe_status:['Universe and eligibility','股票池与资格'],
};
export function readinessTable(l:AgendaLocale){return {headers:l==='zh-CN'?['待补材料','当前状态']:['Pending evidence','Current state'],rows:data.readiness.issue_categories.map(issue=>[tAgenda(issues[issue],l),issue==='calendar'?(l==='zh-CN'?'尚未独立核验官方来源':'Official source not independently verified'):(l==='zh-CN'?'尚无未来形成时点收据':'Future formation receipt unavailable')])};}
const priorities:Record<string,LocalText>={
 missing_amount_requires_primary_notice:['Missing amount needs primary notice','缺少金额，需查原始公告'],announcement_or_period_conflict:['Announcement or period conflict','公告或期间冲突'],economic_conflict:['Economic terms conflict','经济条款冲突'],settlement_or_unknown_date:['Settlement/date conflict','结算或日期冲突'],
};
export function eventFinding(l:AgendaLocale){const e=data.events;return l==='zh-CN'?`两套方案合计有 ${e.dated_unique_blockers} 个不同的已知日期阻塞事件，另有 ${e.unknown_exdate_rows} 行除权日未知。原始来源复查已对 ${e.retrospective_economic_adjudications} 个事件给出经济含义裁定，另有 ${e.dated_unresolved} 个尚未完成复查。原解析器未重算，两套方案的阻塞数仍为 ${e.plan_blockers['45']}／${e.plan_blockers['90']}，真实股份账户仍未就绪。`:`The two plans contain ${e.dated_unique_blockers} distinct dated blocked events, plus ${e.unknown_exdate_rows} row with an unknown ex-date. Primary-source review adjudicates the economics of ${e.retrospective_economic_adjudications} events retrospectively; ${e.dated_unresolved} remain unreviewed. The owner resolver was not recomputed: plan blockers remain ${e.plan_blockers['45']} / ${e.plan_blockers['90']}, and raw-share readiness remains false.`;}
export function eventTable(l:AgendaLocale){return {headers:l==='zh-CN'?['互斥优先组','事件数']:['Mutually exclusive priority group','Events'],rows:Object.entries(data.events.priority_counts).map(([key,count])=>[tAgenda(priorities[key],l),String(count)])};}
export function caseTable(l:AgendaLocale){return {headers:l==='zh-CN'?['真实事件示例','核算教训与边界']:['Real-event example','Accounting lesson and boundary'],rows:[
 [l==='zh-CN'?'普通送转股份':'Ordinary share distribution',l==='zh-CN'?'区分权益与可卖库存。此例除权与上市同日，没有观察到跨日未上市期；延后交割的单元测试另验模型库存限制；实际可卖股数仍未知。':'Separate entitlement from sellable inventory. Ex-date and listing date coincide in this case, so no multi-day unlisted phase is observed; delayed-settlement unit tests check modeled inventory restrictions separately; executable sellable shares remain unknown.'],
 [l==='zh-CN'?'现金分配':'Cash distribution',l==='zh-CN'?'把应收与已结算现金分开。此例除权与派息同日，核算先后阶段不能解释为观察到了日内到账过程。':'Separate receivables from settled cash. Ex-date and payment date coincide; accounting phases do not establish observed intraday payment timing.'],
 [l==='zh-CN'?'重整中原股东无获配':'Restructuring without original-holder allocation',l==='zh-CN'?'公司总股数增加不能直接计入原持有人权益；原始公告未向原股东分配时，此类持有人的新增权益为零。':'A company-level share increase does not automatically create original-holder entitlement. When the primary notice allocates none to original holders, their additional entitlement is zero.'],
 [l==='zh-CN'?'持有人类别不同的差异化现金分配':'Cash distribution by holder class',l==='zh-CN'?'按持有人类别确定税前权益；发行人平均值、除权参考价参数与全局最新记录，都不能替代适用的持有人分配率。':'Gross entitlement depends on holder class. The issuer average, ex-price reference parameters and globally latest row cannot replace the distribution rate applicable to that holder.'],
 ]};}
const caseLabels:Record<string,LocalText>={
 unrestricted_ordinary_capitalization:['Ordinary share distribution','普通送转股份'],
 restructuring_no_original_holder_entitlement:['No original-holder allocation','原股东无获配'],
 gross_ordinary_cash_distribution:['Gross cash distribution','税前现金分配'],
 differential_cash_requires_holder_classification:['Cash by holder class','按持有人类别分配现金'],
};
const shortNum=(value:string,l:AgendaLocale)=>new Intl.NumberFormat(l,{maximumFractionDigits:7}).format(Number(value));
export function caseOutcomeTable(l:AgendaLocale){const zh=l==='zh-CN';return {
 headers:zh?['案例／原始公告','登记／除权／结算日期','每股权益与适用范围','股份、现金与应收变化','P=1 的单位净值']:['Case / primary notice','Record / ex / settlement dates','Entitlement per original share','Shares, cash and receivables','Unit NAV at P=1'],
 rows:data.cases.map(row=>{
 const d=row.dates;const dateText=[`${zh?'登记':'Record'} ${d.record_date}`,`${zh?'除权':'Ex'} ${d.ex_date}`,d.pay_date?`${zh?'派息':'Payment'} ${d.pay_date}`:d.stock_listing_date?`${zh?'上市':'Listing'} ${d.stock_listing_date}`:(zh?'原股东无新增结算':'No new original-holder settlement')].join('; ');
 let terms='',flow='',nav='';
 if('holder_rates' in row){
  terms=zh?'小股东 0.3158 元；指定大股东 0.2650 元；参考价扣减 0.28 元不可作持有人权益':'Minority CNY 0.3158; named large holder CNY 0.2650; reference deduction CNY 0.28 is not holder entitlement';
  flow=zh?'股份 1,000 → 1,000；税前现金 0 → 315.8 或 265；期末应收 0；须先定持有人类别':'Shares 1,000 → 1,000; gross cash 0 → 315.8 or 265; closing receivable 0; holder class required';
  nav='1,000 → 1,315.8 / 1,265';
 }else{
  const points=row.snapshots!;const before=points[0],after=points[points.length-1];
  terms=row.case==='unrestricted_ordinary_capitalization'?(zh?'每原股新增 0.4 股，现金 0':'0.4 additional shares; cash 0'):row.case==='gross_ordinary_cash_distribution'?(zh?'税前 1.23 元；参考价扣减 1.2255331 元不可作权益':'Gross CNY 1.23; reference deduction CNY 1.2255331 is not entitlement'):(zh?'原股东新增股份与现金均为 0':'Original holders receive no new shares or cash');
  flow=`${zh?'股份':'Shares'} ${shortNum(before.settled_shares,l)} → ${shortNum(after.settled_shares,l)}; ${zh?'现金':'cash'} ${shortNum(before.cash,l)} → ${shortNum(after.cash,l)}; ${zh?'期末应收现金／股数':'closing receivable cash/shares'} ${shortNum(after.cash_receivable,l)} / ${shortNum(after.share_receivable,l)}`;
  if('exdate_pre_settlement' in row)flow+=zh?'；同日核算阶段为应收现金 1,230 → 0':' ; same-day accounting phase: receivable cash 1,230 → 0';
  nav=`${shortNum(before.nav,l)} → ${shortNum(after.nav,l)}`;
 }
 return {source:row.source_url,sourceHash:row.source_pdf_sha256,cells:[tAgenda(caseLabels[row.case],l),dateText,terms,flow,nav]};
 })};}
export const exampleSources=data.cases.map(row=>({label:caseLabels[row.case],url:row.source_url,hash:row.source_pdf_sha256}));
export const evidenceMdTable=(table:{headers:string[];rows:string[][]})=>[table.headers,table.headers.map(()=>'---'),...table.rows].map(row=>`| ${row.map(cell=>cell.replaceAll('|','\\|')).join(' | ')} |`).join('\n');
export function nextEvidenceMarkdown(l:AgendaLocale){const t=(key:keyof typeof nextCopy)=>tAgenda(nextCopy[key],l);return [
 `## ${t('title')}`,`### ${t('eventTitle')}`,eventFinding(l),`### ${t('outcomesTitle')}`,t('outcomesBoundary'),evidenceMdTable({headers:caseOutcomeTable(l).headers,rows:caseOutcomeTable(l).rows.map(row=>[`[${row.cells[0]}](${row.source})`,...row.cells.slice(1)])}),evidenceMdTable(eventTable(l)),t('eventBoundary'),evidenceMdTable(caseTable(l)),t('caseBoundary'),`#### ${t('sourcesTitle')}`,t('sourcesBoundary'),...caseOutcomeTable(l).rows.map(row=>`- [${row.cells[0]}](${row.source}) · SHA-256 \`${row.sourceHash}\``),`### ${t('readinessTitle')}`,t('readiness'),evidenceMdTable(readinessTable(l)),t('provenance'),`#### ${t('calendarTitle')}`,t('calendar'),...data.calendar.sources.map(source=>`- [${source.role==='annual'?(l==='zh-CN'?'2026 年全年休市安排':'2026 annual exchange holiday schedule'):(l==='zh-CN'?'国庆节休市安排':'National Day exchange closure notice')}](${source.url}) · SHA-256 \`${source.sha256}\``),`### ${t('gateTitle')}`,t('gate'),t('boundary'),`[${t('download')}](https://runchengxie.github.io/quant-market-research/data/microcap_next_evidence_review.json)`,...Object.entries(data.source_sha256).map(([role,hash])=>`- ${role}: \`${hash}\``),
].join('\n\n');}
