import data from '../../public/data/microcap_chain_review.json';
import type { LocalText } from './microcap-hub';
import { tAgenda, type AgendaLocale } from './microcap-agenda';

export const chainEvidence = data;
export const chainCopy = {
 title: ['From primary notices to a verifiable account chain', '从原始公告走向可核验的账户链'],
 intro: ['Primary notices now cover all seven events that touched retained simulated holdings. They clarify economic terms, but do not certify integer holder inventory, tax or full-period strategy capacity. The owner resolver still reports 83 / 82 blockers; raw-share strategy readiness remains false.', '与保留模拟持仓相交的七个事件，现已全部核对原始公告。公告明确了经济条款，但尚未认证持有人整数股份、税费或完整区间的策略容量。原解析器仍报告 83／82 个阻塞，真实股份策略仍未就绪。'],
 primaryTitle: ['Seven held-event notices reviewed', '七个涉持仓事件的公告核对'],
 primary: ['Six notices explicitly describe fractional-share allocation. One lists newly issued shares after the ex-date. Ex-date, share-credit date and tradability date require separate checks; listing does not establish when shares reached an account. In one case, the final implemented ratio differs from the original proposal after the share base changed: the final implementation terms govern the check.', '六份公告明确了零碎股分配办法；一项新增股份在除权日之后上市。除权日、股份登记到账日与可交易日须分别核对，上市安排不能证明账户何时到账。在一个案例中，股本变化后，最终实施比例与原提案不同，核对应以最终实施条款为准。'],
 primaryBoundary: ['Three capitalization-only schemes do not announce a numeric cash distribution. Their cash field remains null, not zero. Announcement review does not supply each holder’s integer entitlement or tax treatment, and does not recompute the owner resolver.', '三项仅转增股份的方案未公告数值现金分配，现金字段继续保留 null，不能填作零。公告核对不能补出每位持有人的整数权益或税务处理，也没有重算原事件解析器。'],
 traceTitle: ['Conditional absence before activation; record-date inventory still unknown', '启动前的条件性未持仓判断；事件登记日库存仍未知'],
 trace: ['Original source-backed engine files show 63 leading cash sessions for the historical 120-session turnover plan requiring 90 valid observations. This supports six conditional pre-activation absence classifications for that plan only. It does not recover raw-share or fill inventory at the record date: the six unknown classifications in the retained inventory table remain unchanged.', '对历史 120 交易日换手窗口、最低 90 个有效观测的方案，原始引擎文件支持开头有 63 个纯现金交易日。因此，仅对这一方案，可以推导六项启动前的条件性未持仓判断。这没有找回事件登记日的真实股份或成交库存，保留库存表中的六项未知分类不变。'],
 traceBoundary: ['Minimum-45 has one positive preceding-target event, and its fills remain unrecovered. The minimum-90 absence inference cannot be transferred to minimum-45. Source matching narrows the search; it does not authenticate the original full runtime.', '45 观测方案有一项前次目标持仓为正的事件，其成交仍未找回。不能把 90 观测方案的未持仓推断移用于 45 观测方案。来源匹配缩小了查找范围，但没有认证原始完整运行。'],
 targetTitle: ['Replay frozen targets from cash: NAV withheld', '从现金开始重放冻结目标：暂不接受净值'],
 target: ['A portfolio replay starting from cash follows two frozen historical 40-name target formations across 21 sessions, spanning 46 distinct target names. The query scan covers 2,230 source rows; one action is included and one action before entry is excluded. This is a newly constructed slice, not a recovered historical strategy account.', '从现金开始的组合重放在 21 个交易日内跟踪两次冻结的历史目标，每次 40 只，合计 46 只不同股票。查询扫描涉及 2,230 行来源记录，纳入一项事件，并排除一项入场前事件。这是新构造的区间诊断，并未找回历史策略账户。'],
 targetBoundary: ['The general execution engine’s existing contract rounds buys to trading lots, while its continuous partial-sell quantities do not establish raw-share inventory rules. An independent integer/lot guard rejects the candidate. Verification therefore fails closed: no NAV is accepted. This contract gap leaves the whole account uncertified; target and source coverage alone do not clear it.', '通用执行引擎的现有约定只对买入数量取交易单位，连续份额模式的部分卖出数量并不满足真实股份库存规则。独立的整数／交易单位检查拒绝了该候选，因此核验停在失败状态，暂不接受任何净值。这个执行约定缺口仍使整个账户无法认证，目标与来源覆盖齐全也不能解除它。'],
 prospectiveTitle: ['A fresh manual verification, with the register unchanged', '一次新的人工核验，登记册保持不变'],
 prospective: ['The UTC time below records this manual check. The two-entry register and its published head are unchanged; seven input categories remain pending, with zero admitted and zero newly completed windows. No scheduled job is installed.', '下方 UTC 时间记录本次人工检查。登记册仍为两条，已公布末项哈希未变；输入仍有七类待补材料，纳入数量和新完成区间均为零，也未安装定时任务。'],
 prospectiveBoundary: ['The stable production release currently lacks the register CLI. Future operation requires a validated stable release; a temporary development worktree is not an operational release. Missing formation descriptors or signal evidence in the receipt means those materials were not provided for this verification, not that the underlying historical data do not exist.', '当前稳定生产版本尚无登记命令。后续运行需要经过验证的稳定发布版，临时开发工作树不能作为运行发布版。收据缺少形成期说明或信号证据，表示这些材料未向本次核验提供，不能据此判断底层历史数据不存在。'],
 descriptorsTitle: ['Formation evidence required before admission', '纳入前所需的形成期材料'],
 descriptors: ['Provide formation-time evidence for all six input roles: prices and adjustments; turnover and traded amounts; capitalization and valuation; benchmark; industry membership; and universe status. Provide the signal evidence as well, with availability, source and code bindings.', '须提供六类输入的形成期证据：价格与复权、换手与成交额、市值与估值、基准、行业归属、股票池状态，并补齐信号证据及其可得时间、来源与代码绑定。'],
 provenance: ['Aggregate provenance and review boundary', '汇总来源与核验边界'],
 download: ['Download the reviewed account-chain aggregates', '下载已审查的账户链汇总'],
} satisfies Record<string, LocalText>;

const label = (en: string, zh: string, locale: AgendaLocale) => locale === 'zh-CN' ? zh : en;
const metrics = (locale: AgendaLocale, rows: Array<[LocalText, number | string]>) => ({
 headers: label('Reviewed measure|Count or value', '核验项目|数量或取值', locale).split('|'),
 rows: rows.map(([name, value]) => [tAgenda(name, locale), String(value)]),
});
export function primaryTable(locale: AgendaLocale) { return metrics(locale, [
 [['Held events reviewed', '已核对涉持仓事件'], data.primary.reviewed_held_events],
 [['Primary notices', '原始公告'], data.primary.primary_notices],
 [['Explicit fractional allocation methods', '明确零碎股分配办法'], data.primary.explicit_fraction_methods],
 [['Share listing after ex-date', '新增股份晚于除权日上市'], data.primary.listing_after_ex],
 [['Cash amount unspecified (null)', '现金金额未公告（null）'], data.primary.cash_numeric_unspecified],
]); }
export function traceTable(locale: AgendaLocale) { return metrics(locale, [
 [['Events with unknown record-date inventory, unchanged', '事件登记日库存未知，保持不变'], data.trace.dated_inventory_unknown],
 [['Minimum-90 conditional absence only', '仅 90 观测方案的条件性未持仓'], data.trace.derived_pre_activation_cash_absence],
 [['Source-backed leading cash sessions', '原始文件支持的开头纯现金交易日'], data.trace.leading_cash_sessions],
 [['Minimum-45 positive preceding target', '45 观测方案前次目标持仓为正'], data.trace.min45_positive_prior_target_events],
]); }
export function targetSliceTable(locale: AgendaLocale) { return metrics(locale, [
 [['Frozen target formations', '冻结目标形成次数'], data.target_slice.formations],
 [['Target names per formation', '每次形成的目标股票数'], data.target_slice.targets_per_formation],
 [['Distinct target names', '不同目标股票总数'], data.target_slice.distinct_target_names],
 [['Sessions', '交易日数'], data.target_slice.sessions],
 [['Source rows scanned', '扫描来源行数'], data.target_slice.query_rows_scanned],
 [['Included actions', '纳入事件'], data.target_slice.included_actions],
 [['Excluded pre-entry actions', '排除的入场前事件'], data.target_slice.excluded_pre_entry_actions],
 [['Accepted account NAV', '账户净值验收'], data.target_slice.accepted_nav ? label('Accepted', '已接受', locale) : label('Withheld', '暂不接受', locale)],
]); }
export function prospectiveTable(locale: AgendaLocale) { return metrics(locale, [
 [['Actual manual review UTC', '本次人工核验时间 UTC'], data.prospective.actual_review_utc],
 [['Existing register entries', '既有登记条数'], data.prospective.register_entries],
 [['Pending input categories', '待补输入类别'], data.prospective.pending_categories],
 [['Admitted windows', '已纳入区间'], Number(data.prospective.admitted)],
 [['Newly completed windows', '新完成区间'], data.prospective.new_completed_windows],
]); }
export const chainBlocks = [
 {id: 'primary', title: 'primaryTitle', intro: 'primary', boundary: 'primaryBoundary', table: primaryTable},
 {id: 'trace', title: 'traceTitle', intro: 'trace', boundary: 'traceBoundary', table: traceTable},
 {id: 'target', title: 'targetTitle', intro: 'target', boundary: 'targetBoundary', table: targetSliceTable},
 {id: 'prospective', title: 'prospectiveTitle', intro: 'prospective', boundary: 'prospectiveBoundary', table: prospectiveTable},
] as const;
const markdownTable = (table: ReturnType<typeof primaryTable>) => [table.headers, table.headers.map(() => '---'), ...table.rows].map(row => `| ${row.map(cell => cell.replaceAll('|', '\\|')).join(' | ')} |`).join('\n');
export function chainMarkdown(locale: AgendaLocale) {
 const t = (key: keyof typeof chainCopy) => tAgenda(chainCopy[key], locale);
 return [`## ${t('title')}`, t('intro'), ...chainBlocks.flatMap(block => [`### ${t(block.title)}`, t(block.intro), markdownTable(block.table(locale)), t(block.boundary)]),
  `### ${t('descriptorsTitle')}`, t('descriptors'),
  `SHA-256: \`${data.prospective.anchored_head}\``,
  `### ${t('provenance')}`, `[${t('download')}](https://runchengxie.github.io/quant-market-research/data/microcap_chain_review.json)`,
  ...Object.entries(data.source_sha256).map(([role, hash]) => `- ${role}: \`${hash}\``),
 ].join('\n\n');
}
