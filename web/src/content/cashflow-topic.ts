import type { TopicSection } from '../lib/topic-sections';

export const cashflowSections: readonly TopicSection[] = [
  { id: 'cashflow-returns', label: '收益与分红口径', labelEn: 'Returns and dividends', available: true },
  { id: 'cashflow-recovery', label: '回撤与回本', labelEn: 'Drawdowns and recovery', available: true },
  { id: 'cashflow-replication', label: '指数复刻与可交易性', labelEn: 'Index replication and tradability', available: true },
  { id: 'cashflow-long-run', label: '长期回报与分散', labelEn: 'Long-run returns and diversification', available: true },
  { id: 'cashflow-robustness', label: '结论稳定性与ETF', labelEn: 'Robustness and ETF evidence', available: true },
  { id: 'research-method', label: '数据与方法', labelEn: 'Sources and methods', available: true },
];

export const cashflowTopicCopy = {
  recovery: ['Recovery means returning to a prior investment high. Completed and ongoing declines are reported separately; an ongoing interval is a lower bound (right-censored).', '回本指投资回到此前高点。已经回本和截至样本末仍未回本的区间分开记录；尚未回本的观察时长只是下界（右删失）。'],
} as const;

export const cashflowIndexNames: Record<string, string> = {
  '980092.SZ': 'SZSE Free Cash Flow',
  '932365.CSI': 'CSI All-Share Cash Flow',
  '932366.CSI': 'CSI 300 Cash Flow',
  '932367.CSI': 'CSI 500 Cash Flow',
  '932368.CSI': 'CSI 800 Cash Flow',
  '932369.CSI': 'CSI 1000 Cash Flow',
  '931082.CSI': 'CSI A500 Cash Flow',
  '932457.CSI': 'Stock Connect Hong Kong Cash Flow',
};
