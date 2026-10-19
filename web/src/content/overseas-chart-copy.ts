export const overseasChartCopy = {
 axis: ['bp / interval', 'bp／观测间隔'],
 title: ['Cost sensitivity', '费用敏感性'],
 etf: ['ETF', 'ETF'], delay: ['Input availability', '输入可用时间'],
 scheduled: ['Scheduled inputs (lag 0)', '默认时间假设（延迟 0）'], delayed: ['One session later (lag 1)', '延后一个交易日（延迟 1）'],
 cost: ['Total round-trip cost (bp)', '双边合计费用（bp）'], mean: ['Mean net return (bp / observed interval)', '每个观测间隔平均净收益（bp）'],
 help: ['Select an ETF and input delay; hover or tap a point for exact values. Toggle rules in the legend. Lines connect reviewed cost assumptions, not a time series.', '选择 ETF 和输入延迟，悬停或点按查看数值；点击图例切换持仓规则。连线仅连接已审阅的费用假设，不是时间序列。'],
 window510300: ['510300: 2020–2026, partial 2026 through October 16.', '510300：2020—2026，2026 年仅截至 10 月 16 日。'],
 window512480: ['512480: 2021–2026, partial 2026 through October 16. ETF sample windows differ.', '512480：2021—2026，2026 年仅截至 10 月 16 日。两只 ETF 样本窗口不同。'],
 caption: ['Cost assumptions vary across the horizontal axis; CNY 1m fixed reference notional. Historic daily-bar proxy returns are not verified fills.', '横轴为不同双边费用假设，固定参考金额为 100 万元。历史日线代理收益并非已核实成交。'],
 table: ['Selected cost scenarios and sample sizes', '当前选择的费用情景与样本量'], model: ['Exposure rule', '持仓规则'], n: ['Observed intervals', '观测间隔数'], missing: ['Not reported', '未提供'], download: ['Download static chart (SVG)', '下载静态图（SVG）'], fallback: ['Static chart and full numeric evidence remain available without JavaScript.', '未启用 JavaScript 时可查看静态图及完整数值证据。'],
} as const;
