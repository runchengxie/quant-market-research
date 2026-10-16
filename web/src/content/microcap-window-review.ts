import type { LocalText } from './microcap-hub';
export const windowReviewCopy = {
 title:['Window reproduction check · 2026-10-16','窗口复算核对 · 2026-10-16'],
 finding:['The new run matches all four rounded published metrics for 20 and 60 sessions. The 120-session result differs materially: net annual return is 4.22%, versus the published 7.60%. The original ascending return ordering is not reproduced.','新运行中，20 日与 60 日的四项主要指标均匹配公开舍入值；120 日明显不一致：净年化为 4.22%，原公开值为 7.60%。原图中收益随窗口递增的排序没有重现。'],
 scope:['New observation, not recovered historical execution: 2,778 return sessions; 2015-01-01–2026-07-31 input scope; current input vintage with retained monthly controls. Monthly, 40 targets, 60-name buffer, 180-day listing minimum, assumed 10 bp per traded notional. Lagged 20/60/120-session means require 15/45/90 observations. Continuous weight accounting; no lot size, market impact or capacity calibration.','这是新观察，并非找回原始历史执行：2,778 个收益观测日；输入范围 2015-01-01—2026-07-31，当前版本输入配合保留的月度控制变量。月频、40 只目标、60 只缓冲、上市至少 180 日，假设按成交金额收取 10bp；滞后 20／60／120 日均值分别要求 15／45／90 个观测。使用连续权重核算，未校准整手、冲击或容量。'],
 boundary:['The completed receipt binds code, locked dependencies and before/after input hashes. Count checks match the retained cache, but do not prove historical byte identity. ST history is reconstructed and not revision-safe. The 60-session stored daily series independently replays its original metrics; historical 20/120 daily artifacts and a joint original runtime receipt remain missing. The original minimum-observation convention is unbound: the helper default is 45, while this run uses 75% window support. The 120-session arm first trades 2015-06-01. Warm-up differences are a hypothesis, not an established explanation. Keep both vintages; investigate the 120-session discrepancy before using that ranking.','完成收据记录代码、锁定依赖及运行前后输入哈希；行数检查与保留缓存相符，仍不证明历史字节相同。ST 历史属于重建口径，不能保证不受后续修订影响。另已用保留日度序列独立回放 60 日指标；20／120 日历史逐日制品和原始统一运行收据仍缺。原运行的最低观测数约定未能绑定：辅助函数默认为 45，本次明确要求窗口的 75%；120 日组首次交易为 2015-06-01。预热规则差异目前仅是假说。两版结果均保留，在解释排序前须查清 120 日差异。'],
 source:['New run: low-turnover-windows-9d92f18f-b2d9-43d0-924b-237572f635a3; driver SHA-256 8316cdd8c9416f2c7cc5e35d43b14337967590c9f539051c37170f47f9568483. Input and code hashes remained unchanged during execution.','新运行：low-turnover-windows-9d92f18f-b2d9-43d0-924b-237572f635a3；驱动 SHA-256：8316cdd8c9416f2c7cc5e35d43b14337967590c9f539051c37170f47f9568483。运行前后输入与代码哈希一致。'],
} satisfies Record<string,LocalText>;
export const windowRecheck = [
 {days:20,old:[3.519612,.263731,-65.009288,11.592836],fresh:[3.519612189781296,.2637305890749733,-65.009287526075,11.592835756203035]},
 {days:60,old:[5.334535,.330517,-52.389378,6.785942],fresh:[5.3345345551543355,.33051701423170293,-52.38937783294797,6.785941502347826]},
 {days:120,old:[7.601898,.411345,-45.607451,4.474725],fresh:[4.2245132043773115,.2890227592122959,-58.25987592675094,4.4406538532280795]},
];
export function windowReviewTable(locale:'en-US'|'zh-CN') {
 const zh=locale==='zh-CN';
 return {headers:zh?['窗口（日）','版本','净年化 %','夏普','净回撤 %','年换手 倍']:['Window (sessions)','Vintage','Net annual %','Sharpe','Net drawdown %','Annual turnover ×'],rows:windowRecheck.flatMap(r=>[['old',r.old],['fresh',r.fresh]].map(([key,values])=>[String(r.days),key==='old'?(zh?'原公开快照':'Published snapshot'):(zh?'2026-10-16 新运行':'New 2026-10-16 run'),...(values as number[]).map(v=>v.toFixed(6))]))};
}
export function windowReviewMarkdown(locale:'en-US'|'zh-CN') {
 const i=locale==='zh-CN'?1:0,table=windowReviewTable(locale);
 return [`### ${windowReviewCopy.title[i]}`,...(['finding','scope','boundary','source'] as const).map(k=>windowReviewCopy[k][i]),[table.headers,table.headers.map(()=>'---'),...table.rows].map(r=>`| ${r.join(' | ')} |`).join('\n')].join('\n\n');
}
