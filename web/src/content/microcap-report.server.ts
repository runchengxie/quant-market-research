import { chainMarkdown } from './microcap-chain';
import { impactMarkdown } from './microcap-impact';
import { nextEvidenceMarkdown } from './microcap-next-evidence';
import { statusMarkdown } from './microcap-status';
import { agendaMarkdown } from './microcap-agenda';
import { followupMarkdown } from './microcap-followup';
import { windowReviewMarkdown } from './microcap-window-review';
import { comparisonMarkdown } from './microcap-comparison.server';
import { editionMarkdown, timelineMarkdown } from './microcap-editions.server';
import { historyMarkdown, historicalTablesMarkdown, recoveryMarkdown, type HistoricalSnapshot } from './microcap-history-report';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { hubCopy, researchQuestions, revisions, openQuestions, type LocalText } from './microcap-hub';
import { publicDocs } from './public-registry';
import { englishCopy } from './locale-copy';
import { resolveDocLink } from './rehype-public-docs';

export type ReportLocale = 'en-US' | 'zh-CN';
const origin = 'https://runchengxie.github.io/quant-market-research';
const reviewedOn = '2026-10-18';
// Explicit publication allowlist: no directory scanning or private research reads.
const reportSources = ['microcap-method', 'low-turnover-method', 'microcap-execution-diagnostic', 'smallcap-turnover-history'];
const text = (value: LocalText, locale: ReportLocale) => value[locale === 'zh-CN' ? 1 : 0];
const cell = (value: string) => value.replaceAll('|', '\\|').replaceAll('\n', ' ');
const table = (headers: string[], rows: string[][]) => [headers, headers.map(() => '---'), ...rows].map(row => `| ${row.map(cell).join(' | ')} |`).join('\n');
export async function readReportSnapshot() {
  return JSON.parse(await readFile(resolve(process.cwd(), 'public/data/low_turnover_exploration.json'), 'utf8')) as HistoricalSnapshot & {
    generated_at: string; coverage: {start: string; end: string};
    window_sensitivity: Array<{window_days: number; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number}>;
    joint_matrix: Array<{turnover_definition: string; rebalance_frequency: string; net_annual_return: number}>;
  };
}
export async function buildMicrocapReport(locale: ReportLocale) {
  const zh = locale === 'zh-CN';
  const t = (en: string, cn: string) => zh ? cn : en;
  const snapshot = await readReportSnapshot();
  const sources = reportSources.map(id => publicDocs.find(doc => doc.id === `${id}${zh ? '-zh-CN' : ''}`)!);
  const title = t('Small- and micro-cap research: evidence, methods and open questions', '小微盘研究整理：证据、方法与待解问题');
  const sections = [
    `# ${title}`,
    t(`Public evidence review: ${reviewedOn}. This editorial date is not a data cutoff. The portfolio snapshot was generated on ${snapshot.generated_at}, covering ${snapshot.coverage.start} to ${snapshot.coverage.end}; each appendix retains its own dates. Stored exclusion results were reviewed without rerunning that experiment. Separately identified window checks do not overwrite historical outputs.`, `公开证据整理日期：${reviewedOn}。这不是统一的数据截止日期。组合快照生成于 ${snapshot.generated_at}，覆盖 ${snapshot.coverage.start} 至 ${snapshot.coverage.end}；各附录保留各自日期。排除实验使用保留结果审查，未重跑该实验；单独标识的窗口检查不覆盖历史输出。`),
    t('This report assembles the reviewed public record. It is not an inventory of every private experiment or a statement of strategy readiness. Missing comparisons remain open questions. All figures are historical, modeled or source-reported within their stated scope.', '本报告汇编已审查的公开证据与研究历史概括，不等于列举全部私有实验，也不代表策略已具备部署条件。缺失的对照继续保留为待解问题；各项数字按其范围分别属于历史观察、模拟或来源报告。'),
    `## ${t('Current conclusion', '当前结论')}`,
    t('The clearest micro-cap finding is substantial downside risk and potentially long recovery waits. Returns remain sensitive to eligibility, missing quotes, execution clocks and portfolio construction. Low turnover has historical conditional associations, but an independent causal premium and practical capacity have not been established.', '目前较清楚的微盘发现是：下行风险大，回本等待可能很长。收益仍受资格筛选、缺失报价、执行时点与组合构造影响。低换手存在历史条件关联，但独立因果溢价和实际容量尚未确立。'),
    t('The fixed monthly low-turnover simulation reports net annual returns of 3.52%, 5.33% and 7.60% for 20-, 60- and 120-session windows. The new 120-session run gives 4.22% with 90 valid observations; a same-input sensitivity with 45 gives 6.26%. The threshold changes the result but does not identify the historical method or fully explain the gap. These inspected figures are not a prospective ranking.', '固定月频低换手模拟中，20、60、120 日窗口净年化分别为 3.52%、5.33%、7.60%。120 日新运行按 90 个有效观测得到 4.22%；同一输入改为 45 个观测后为 6.26%。门槛会改变结果，但仍无法确认历史方法，也没有完全解释差距。这些已查看的数字不是前瞻排名。'),
    statusMarkdown(locale),
    `## ${t('Contents', '阅读顺序')}`,
    t('0. Primary notices, account-chain verification and unchanged manual register\n0. Version 1.0.6 holdings-impact snapshot and version 1.0.5 event/readiness snapshot\n0. New evidence, prospective protocol and claim review\n0. Follow-up findings (2026-10-17)\n1. Research map and evidence status\n2. Comparable portfolio definitions\n3. Turnover-window comparison\n4. Definition × rebalance matrix\n5. Research history and coverage register\n6. All published snapshot table families\n7. Revisions and limits\n8. Open questions and resumption criteria\n9. Public methodology appendices and sources', '0. 原始公告、账户链核验与未变的人工登记\n0. 1.0.6 版持仓影响快照与 1.0.5 版事件／就绪快照\n0. 新增证据、前瞻协议与结论复查\n0. 后续核查（2026-10-17）\n1. 研究地图与证据状态\n2. 可比较的组合定义\n3. 换手窗口对照\n4. 换手定义 × 调仓频率矩阵\n5. 研究历史与覆盖清单\n6. 公开快照完整表组\n7. 修正记录与局限\n8. 待解问题与恢复研究条件\n9. 公开方法附录与来源'),
    chainMarkdown(locale), impactMarkdown(locale), nextEvidenceMarkdown(locale), agendaMarkdown(locale), followupMarkdown(locale),
    editionMarkdown(locale),
    `## ${text(hubCopy.title, locale)}`,
    ...researchQuestions.map(q => `### ${text(q.title, locale)}\n\n**${text(q.status, locale)}**\n\n${text(q.finding, locale)}\n\n**${text(hubCopy.sample, locale)}：** ${text(q.sample, locale)}\n\n**${text(hubCopy.next, locale)}：** ${text(q.next, locale)}\n\n[${text(q.action, locale).replace(/[↓↗]/g, '').trim()}](${origin}${q.href.startsWith('#') ? '/research/microcap/' : ''}${q.href})`),
    `## ${t('Keep portfolio definitions separate', '组合口径对照')}`,
    table(t('Object|Formation and return basis|Purpose and limit', '对象|形成与收益口径|用途与限制').split('|'), [
      [t('Vendor reference index', '供应商参考指数'), t('Provider points and available membership; dividend conventions need review', '供应商点位与可得成分；分红口径需核对'), t('Reference comparison, not an executable account', '用于参照，不代表可执行账户')],
      [t('Smallest-N reconstruction', '最小 N 重建'), t('Post-close ranking, next-session close execution, following close valuation; early and cleaned sources kept separate', '收盘后排名，次一交易日收盘执行，再下一交易日收盘计价；早期与清洗来源分开'), t('Historical return and risk with explicit missing-price policies', '在明确缺价规则下描述历史收益与风险')],
      [t('Low-turnover candidate', '低换手候选'), t('Monthly; 40 target names, 60-name buffer, 10 bp fee in the window comparison', '窗口对照为月频、40 只目标、60 只缓冲、10bp 交易费'), t('Portfolio sensitivity; not the cross-sectional low-minus-high spread', '组合敏感性，不等于截面低减高收益差')],
      [t('Small-cap plus low-turnover composite', '小盘加低换手复合组合'), t('Definition × cadence grid from a historical weight-level screening engine', '历史权重筛选模拟的定义与频率矩阵'), t('Requires consistent share-ledger confirmation before selection', '选型前需一致份额账本复核')],
      [t('Public execution diagnostic', '公共执行诊断'), t('Separate continuous holdings and cash; 5% participation, T+1, price limits, assumed 5 bp cost', '独立持续持仓与现金；5% 参与率、T+1、涨跌停、假设 5bp 成本'), t('Short-sample mechanism check; not full historical performance or certified capacity', '短样本机制检查，不是完整历史业绩或容量认证')],
    ]),
    `## ${text(hubCopy.windows, locale)}`,
    text(hubCopy.windowIntro, locale), text(hubCopy.windowScope, locale),
    `![${text(hubCopy.windows, locale)}](${origin}/downloads/microcap-windows.${locale}.svg)`,
    table([text(hubCopy.days, locale), text(hubCopy.return, locale), text(hubCopy.drawdown, locale), 'Sharpe', text(hubCopy.turnover, locale)], snapshot.window_sensitivity.map(row => [String(row.window_days), `${Number(row.net_annual_return).toFixed(2)}%`, `${row.net_max_drawdown.toFixed(2)}%`, row.net_sharpe.toFixed(3), `${row.annualized_turnover.toFixed(2)}×`])),
    text(hubCopy.windowCaveat, locale), windowReviewMarkdown(locale),
    `## ${text(hubCopy.matrix, locale)}`, text(hubCopy.matrixIntro, locale), text(hubCopy.matrixBoundary, locale),
    table([t('Definition', '换手定义'), ...['weekly','biweekly','monthly','quarterly'].map(id => text(hubCopy[id as 'weekly'], locale))], ['mean_20','mean_60','median_60','mean_120'].map(id => [text(hubCopy[({mean_20:'mean20',mean_60:'mean60',median_60:'median60',mean_120:'mean120'} as const)[id as 'mean_20']],locale), ...['weekly','biweekly','monthly','quarterly'].map(cadence => {const row=snapshot.joint_matrix.find(r=>r.turnover_definition===id&&r.rebalance_frequency===cadence);return row ? `${Number(row.net_annual_return).toFixed(2)}%` : t('Missing','缺失');})])),
    await comparisonMarkdown(locale), timelineMarkdown(locale),
    historyMarkdown(locale), recoveryMarkdown(locale), historicalTablesMarkdown(snapshot, locale),
    `## ${text(hubCopy.revisions, locale)}`, text(hubCopy.revisionsIntro, locale), ...revisions.map(item=>`### ${text(item.title,locale)}\n\n${text(item.text,locale)}`),
    `## ${text(hubCopy.open,locale)}`, ...openQuestions.map(item=>`### ${text(item.title,locale)}\n\n${text(item.text,locale)}`),
    `### ${t('What would justify stronger conclusions?', '什么证据能支持更强的结论？')}`,
    t('Resume a return comparison only after the same universe, formation clock, source versions, benchmark, missing-price policy and held-share accounting reconcile. Capacity claims require fills, cash, costs and delayed-order opportunity costs under calibrated impact. Mechanism claims need common-support controls and prospective evidence; stage differences alone do not establish causal effects. Preserve failed and inconclusive tests.', '恢复收益比较前，先核对同一股票池、形成时点、来源版本、基准、缺价规则与持有份额核算。容量解释需要在校准冲击下核对成交、现金、成本和延迟订单机会成本。机制解释需要共同样本控制和前瞻证据，阶段差异本身不能证明因果。失败与不确定的检验继续保留。'),
    `## ${t('Sources and version boundaries', '来源与版本边界')}`,
    `- [${t('Interactive research page','交互研究页面')}](${origin}/research/microcap/)\n- [${t('Published exploratory snapshot','公开探索快照')}](${origin}/data/low_turnover_exploration.json)`,
    t('The appendices below preserve the selected public language records in full. English and Chinese companions are not always equally detailed: the Chinese execution note contains additional historical receipts. Language selection does not certify equivalence of samples or authorize reusing superseded figures. Read correction notices beside their source results.', '以下附录完整保留所选语言的公开记录。中英文历史文档详略并非完全一致：中文执行记录包含更多历史收据。选择语言不代表不同样本可比，也不代表旧数字可以复用。历史结果应与旁边的修正说明一起阅读。'),
  ];
  for (let i=0;i<sources.length;i++) {
    const doc=sources[i];
    const body=await readFile(resolve(process.cwd(),'..',doc.source),'utf8');
    const absolute=body.replace(/\[([^\]]+)\]\(([^)]+)\)/g,(all,label,href)=> {
      if (/^(https?:|mailto:|#)/.test(href)) return all;
      return `[${label}](${resolveDocLink(doc.source,href,origin)})`;
    }).replace(/^(#{1,5}) /gm, '$1# ');
    sections.push(`## ${t('Appendix','附录')} ${i+1} · ${zh ? doc.title : englishCopy(doc).title}`, `[${t('Canonical web source','网页来源')}](${origin}${doc.route})`, absolute);
  }
  return { title, markdown: sections.join('\n\n').trimEnd()+'\n' };
}
export async function buildWindowSvg(locale: ReportLocale) {
  const snapshot=await readReportSnapshot();
  const zh=locale==='zh-CN';
  const rows=snapshot.window_sensitivity;
  const max=Math.max(...rows.map(row=>row.net_annual_return));
  return `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="340" viewBox="0 0 800 340" role="img" aria-labelledby="title desc"><title id="title">${zh?'换手窗口与净年化收益':'Turnover window and net annual return'}</title><desc id="desc">${rows.map(row=>`${row.window_days}: ${Number(row.net_annual_return).toFixed(2)}%`).join('; ')}</desc><rect width="800" height="340" fill="var(--surface,#fff)"/><g font-family="sans-serif" fill="var(--ink,#252525)"><text x="30" y="40" font-size="22">${zh?'低换手窗口对照：净年化收益':'Low-turnover windows: net annual return'}</text>${rows.map((row,i)=>`<text x="30" y="${95+i*65}" font-size="18">${row.window_days} ${zh?'日':'days'}</text><rect x="150" y="${75+i*65}" height="25" width="${row.net_annual_return/max*500}" fill="var(--accent-strong,#1267d6)"/><text x="${160+row.net_annual_return/max*500}" y="${95+i*65}" font-size="18">${Number(row.net_annual_return).toFixed(2)}%</text>`).join('')}<text x="30" y="292" font-size="14">${zh?'2015–2026；月频，40 只目标、60 只缓冲；10bp 假设交易费':'2015–2026; monthly, 40 target names / 60-name buffer; assumed 10 bp fee'}</text><text x="30" y="318" font-size="14">${zh?'原快照：2026-09-16；120 日新核对为 4.22%，与图中不同。':'Snapshot 2026-09-16; 120-session value differs in 2026-10-16 recheck (4.22%).'}</text></g></svg>`;
}

export async function buildCandidateSvg(locale: ReportLocale) {
  const snapshot=await readReportSnapshot();
  const zh=locale==='zh-CN';
  const labels=zh?['小盘','低换手','残差换手','行业残差换手','复合','残差复合','行业残差复合','大盘对照','低波动对照']:['Small cap','Low turnover','Residual turnover','Industry residual','Composite','Residual composite','Industry composite','Large-cap control','Low-vol control'];
  const escape=(s:string)=>s.replaceAll('&','&amp;').replaceAll('<','&lt;');
  const zero=470, scale=17;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="850" height="530" viewBox="0 0 850 530" role="img" aria-labelledby="candidate-title candidate-desc"><title id="candidate-title">${zh?'九个历史候选的净年化收益':'Net annual return of nine historical candidates'}</title><desc id="candidate-desc">${snapshot.candidates.map((r,i)=>`${labels[i]}: ${Number(r.net_annual_return).toFixed(2)}%`).join('; ')}</desc><rect width="850" height="530" fill="var(--surface,#fff)"/><g font-family="sans-serif" fill="var(--ink,#252525)"><text x="24" y="35" font-size="22">${zh?'历史候选对照：净年化收益':'Historical candidates: net annual return'}</text><line x1="${zero}" x2="${zero}" y1="55" y2="445" stroke="var(--ink,#252525)"/>${snapshot.candidates.map((r,i)=>{const value=Number(r.net_annual_return),width=Math.abs(value)*scale;return `<text x="24" y="${83+i*43}" font-size="17">${escape(labels[i])}</text><rect x="${value<0?zero-width:zero}" y="${63+i*43}" width="${width}" height="25" fill="var(--accent-strong,#1267d6)"/><text x="${value<0?zero-width-70:zero+width+8}" y="${82+i*43}" font-size="16">${value.toFixed(2)}%</text>`;}).join('')}<text x="24" y="480" font-size="14">${zh?'公开快照：2026-09-16；历史模拟，费用与执行假设未作实盘校准':'Public snapshot: 2026-09-16; historical simulation, uncalibrated fees and execution'}</text><text x="24" y="508" font-size="14">${zh?'保留失败候选；柱长表示收益，不表示可信度或前瞻排名':'Failed candidates retained; bars encode return, not confidence or a prospective ranking'}</text></g></svg>`;
}
