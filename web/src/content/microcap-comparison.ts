import type { LocalText } from './microcap-hub';
export type ComparisonLocale = 'en-US' | 'zh-CN';
export const comparisonText = (value: LocalText, locale: ComparisonLocale) => value[locale === 'zh-CN' ? 1 : 0];
export const comparisonCopy = {
 dataDownload: ['Download reviewed aggregate JSON, including all 288 yearly rows and source hashes','下载经审查的聚合 JSON（含全部 288 行年度输入及来源哈希）'],
 title: ['What survives excluding the smallest stocks?', '剔除最小市值股票后，哪些结果仍然成立？'],
 status: ['Recovered historical outputs · reviewed 2026-10-16 · no research rerun', '找回的历史结果 · 2026-10-16 审阅 · 未重跑研究'],
 finding: ['Dependence on the smallest stocks varies by candidate. With a buffer and equal weights, excluding 30% changes small-cap net annual return from 5.24% to −2.17%, low turnover from 5.33% to 7.76%, and the composite from 11.28% to 9.71%. These are portfolio sensitivities, not evidence of a causal premium.', '对最小市值股票的依赖因候选而异。在缓冲、等权口径下，剔除最小的 30% 后，小盘净年化由 5.24% 降至 −2.17%，低换手由 5.33% 升至 7.76%，复合组合由 11.28% 降至 9.71%。这是组合敏感性，不是因果溢价证据。'],
 weighting: ['Weighting matters: value-weighted low turnover is negative at every exclusion level, while the composite stays positive under both weighting modes. The 10% composite peak is an inspected grid result, not a validated optimum.', '权重方式影响明显：市值加权低换手在全部剔除比例下均为负，复合组合在两种权重下仍为正。复合组合在 10% 处的峰值只是已查看网格的结果，不代表已确认的最优参数。'],
 buffers: ['Buffers lower turnover in all 24 candidate comparisons, but improve net annual return in only 8. Lower trading does not guarantee a better net result. Full tables retain every reviewed comparison.', '缓冲在全部 24 组候选对照中都降低换手，但仅 8 组净年化提高。少交易并不保证净收益更高；完整表保留全部已审阅对照。'],
 scope: ['Input scope 2015-01-01–2026-07-31; 138 monthly formation dates, 2015-02-27–2026-07-31. Candidate comparisons share 2,778 return sessions. The input start is not the first return date; exact daily return endpoints are not retained in these tables.', '输入范围为 2015-01-01—2026-07-31；138 个月频形成日，覆盖 2015-02-27—2026-07-31。候选对照共用 2,778 个收益观测日。输入起点不等于首个收益日，这些表未保留逐日收益的精确首尾日期。'],
 method: ['Exclusions remove 0%, 10%, 20% or 30% of eligible names ranked by formation-date total market capitalization, not that share of market value. The current protocol reconstructs formation-date A-share eligibility with 180 listed days, positive traded amount, non-ST status and finite positive capitalization. Signals are recomputed after exclusion. The protocol specifies 40 monthly targets and a 60-name retention band, with weighting on the same selected names; historical run parameters are not fully authenticated.', '按形成日总市值排序，剔除合格股票数量的 0%、10%、20% 或 30%，不是剔除相同比例的总市值。当前协议按形成日重建 A 股资格，要求上市满 180 天、成交额为正、非 ST、总市值有限且为正；剔除后重新计算信号。协议规定月频目标为 40 只、缓冲保留范围为前 60 只，两种权重使用相同入选股票；历史运行参数尚未全部认证。'],
 provenance: ['Historical fees were not recorded in the retained manifest; the current protocol default of 10 bp is not an authenticated historical fee. Both historical owner-code revisions are unknown. Net results are retained post-cost outputs, not independently reproduced performance.', '保留清单未记录历史费率；当前协议默认 10bp，不等于已核实的历史费率。两个历史代码版本均未知。净收益属于保留的扣费输出，尚未独立复现。'],
 eras: ['Development has 2,154 sessions through 2023; the later 2024–July 2026 sample has 624 and has been inspected. Era returns are compounded from retained yearly rows. Registration-period differences are descriptive and do not identify a policy effect.', '截至 2023 年的开发阶段有 2,154 个观测日；2024 年至 2026 年 7 月阶段有 624 个，现已查看。阶段收益由保留的年度行复合计算。注册制时期差异仅作描述，不能识别政策效果。'],
 capacity: ['Capacity rows use a separate cash-ledger engine with modeled participation, lots, T+1 and delayed execution. They are not a haircut on the weight-engine returns. Exact capacity return dates and observation counts are unbound; simulated results do not certify live capacity.', '容量表使用独立现金账本引擎，模拟参与率、整手、T+1 与延迟执行，不能视为权重引擎收益的简单折减。容量收益的精确日期与观测数未绑定，模拟结果不等于实盘容量认证。'],
 tables: ['All reviewed aggregate rows', '全部已审阅汇总行'],
 download: ['Download chart (SVG)', '下载图表（SVG）'],
 units: ['Returns and drawdowns: %. Cost drag: percentage points. Sharpe: unitless. Turnover: annual multiples; fill and cash: %. All chart facets use the same linear scale and include zero.', '收益与回撤：%；成本拖累：百分点；夏普：无量纲；换手：年倍数；成交与现金比例：%。四幅图共用线性刻度并包含零点。'],
 chart: ['Net annual return across exclusions', '不同剔除比例下的净年化收益'],
 axis: ['Smallest eligible names excluded (%)', '剔除最小市值股票数量（%）'],
 small_cap: ['Small cap', '小盘'], low_turnover: ['Low turnover', '低换手'], composite: ['Composite', '复合组合'],
 equal: ['Equal weight', '等权'], value: ['Value weight', '市值加权'], buffered: ['Buffered', '缓冲'], no_buffer: ['No buffer', '无缓冲'],
 development: ['Development through 2023', '截至 2023 年开发阶段'], later_descriptive: ['Inspected 2024–July 2026', '已查看的 2024—2026 年 7 月'],
 pre_registration_pilot: ['Before registration pilot', '注册制试点前'], registration_pilot: ['Registration pilot', '注册制试点期'], full_registration: ['Full registration', '全面注册制时期'],
} satisfies Record<string, LocalText>;
