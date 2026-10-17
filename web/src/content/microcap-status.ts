import { agenda, claimStages, claimTranslations, tAgenda, type AgendaLocale } from './microcap-agenda';
import type { LocalText } from './microcap-hub';

export const statusCopy = {
 title: ['Current research status', '当前研究状态'],
 intro: ['Read the conclusion and evidence stage first; linked sections retain sample boundaries and the full review record. A completed query is not a settled event or an executable account.', '先看结论和证据阶段；链接章节保留样本边界与完整复查记录。查询完成不等于事件已结算，也不等于账户可执行。'],
 headers: [['Claim', 'Conclusion now', 'Evidence stage', 'Latest evidence', 'Next decisive validation'], ['结论编号／主题', '当前判断', '证据阶段', '最近证据', '下一项关键验证']],
} as const;
const conclusions: Record<string, LocalText> = {
 'MC-C01': ['Large drawdowns and long recovery waits are observed.', '历史上出现过大幅回撤与漫长回本等待。'],
 'MC-C02': ['A conditional historical association remains; causality is unestablished.', '历史条件关联仍在；因果解释尚未确立。'],
 'MC-C03': ['Executable raw-share capacity is not established.', '真实股份账户的可执行容量尚未确立。'],
 'MC-C04': ['Support rules change scores even without buffers.', '即使移除缓冲，观测门槛仍改变得分。'],
 'MC-C05': ['Frozen-target request coverage is complete; settlement remains open.', '冻结目标的请求覆盖已齐；结算核对仍未完成。'],
 'MC-C06': ['The original 120-session runtime remains unrecovered.', '120 日历史原始运行仍未找回。'],
};
const latest: Record<string, LocalText> = {
 'MC-C01': ['Eight retained synthetic-share scenarios document the worst episodes.', '八种保留的合成份额情景记录了最深回撤案例。'],
 'MC-C02': ['Official schedule checked; seven future-input categories remain pending.', '官方交易日安排已核对，前瞻输入仍有七类待补材料。'],
 'MC-C03': ['Three economic reviews; owner blockers remain 83 / 82.', '三项经济含义复查完成，原解析器阻塞仍为 83／82。'],
 'MC-C04': ['Same-input interventions retain shared raw-mean parity.', '同输入干预保留共同原始均值一致性。'],
 'MC-C05': ['Full-window query-evidence gaps are zero in both frozen plans.', '两套冻结方案的完整区间查询证据缺口均为零。'],
 'MC-C06': ['Threshold sensitivity narrows the return gap without identifying the run.', '门槛敏感性缩小收益差距，但没有确认运行身份。'],
};
const next: Record<string, LocalText> = {
 'MC-C01': ['Reconcile the same episodes in raw shares and cash.', '用真实股份与现金账本复核同一批案例。'],
 'MC-C02': ['Observe new eligible frozen intervals; completed months remain zero.', '等待新的合格冻结区间；已完成月份仍为零。'],
 'MC-C03': ['Reconcile primary events, entitlement, settlement and raw marks before capital/cost reruns.', '先核对原始事件、权益、结算与原始价格计价，再重跑资金／成本检验。'],
 'MC-C04': ['Preserve parity under changes to features, support and scoring.', '特征、观测门槛或评分变化后重新核对一致性。'],
 'MC-C05': ['Independently audit announcements, dates and entitlements.', '独立核对公告、日期与权益。'],
 'MC-C06': ['Recover a bound original invocation, code, inputs and daily outputs.', '找回相互绑定的原始调用、代码、输入与逐日输出。'],
};
const links: Record<string, string> = {'MC-C01':'#microcap-research-agenda','MC-C02':'#microcap-next-evidence','MC-C03':'#microcap-next-evidence','MC-C04':'#microcap-followup','MC-C05':'#microcap-followup','MC-C06':'#microcap-window-evidence'};
export function statusRows(locale: AgendaLocale) {
 return agenda.claims.map(row => ({id:row.id, href:links[row.id], title:tAgenda(claimTranslations[row.id].title,locale), cells:[conclusions[row.id],claimStages[row.stage],latest[row.id],next[row.id]].map(value=>tAgenda(value,locale))}));
}
export function statusMarkdown(locale: AgendaLocale) {
 const headers = statusCopy.headers[locale==='zh-CN'?1:0];
 const rows = statusRows(locale).map(row=>[`[${row.id} · ${row.title}](https://runchengxie.github.io/quant-market-research/research/microcap/${row.href})`,...row.cells]);
 return [`## ${tAgenda(statusCopy.title,locale)}`,tAgenda(statusCopy.intro,locale),[headers,headers.map(()=>'---'),...rows].map(row=>`| ${row.map(cell=>cell.replaceAll('|','\\|')).join(' | ')} |`).join('\n')].join('\n\n');
}
