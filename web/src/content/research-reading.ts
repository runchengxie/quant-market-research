export type Copy = readonly [string, string];
export type ReadingSummary = {
  id: string; route: string; title: Copy; conclusion: Copy; scope: Copy; limit: Copy;
  stage: 'description' | 'exploration'; coverage: Copy; date: string | null;
  sources: { path: string; sha256: string }[]; related: string[];
};
export const readingCopy = {
  stage: ['Research stage', '研究阶段'],
  description: ['Historical description', '历史描述'], exploration: ['Historical exploration', '历史探索'],
  coverage: ['Sample dates', '样本日期'], scope: ['What is compared', '比较口径'],
  limit: ['Main unresolved question', '主要待解问题'], sources: ['Data and versions', '数据与版本'],
  archive: ['Methods and research history', '方法与研究历史'],
  summary: ['Research summary', '研究摘要'],
  summaryLink: ['Summary and image export', '研究摘要与单张图片'],
  missing: ['Not provided', '未提供'], date: ['Evidence record date', '证据版本日期'],
  guide: ['Read the figures', '图表怎么看'],
  units: ['A change from 5% to 6% is 1 percentage point. One basis point is 0.01 percentage points. Monthly and annualized returns use different periods.', '5% 到 6% 相差 1 个百分点。1 基点等于 0.01 个百分点。月度收益和年化收益对应不同期间。'],
  costs: ['Gross returns exclude trading costs. Net returns include only the costs explicitly listed in the experiment. Neither label alone establishes real fills.', '毛收益未扣交易成本。净收益只扣除了该实验列出的费用，仍须查看成交假设。'],
  catalog: ['Current findings by topic', '各专题目前发现了什么'],
  intro: ['Open a current report, then follow its methods and history. Dates describe each sample separately.', '从当前报告进入，再查看方法与历史记录。各专题分别标注样本日期。'],
  recent: ['Reading update · 22 October 2026', '阅读方式更新 · 2026 年 10 月 22 日'],
  recentBody: ['Low-turnover and valuation reports clarify their evidence limits. This editorial update adds no new return observations.', '低换手与低估值报告已改写证据说明。本次文字和页面调整没有增加新的收益观察。'],
  sourceNote: ['Selected key public evidence files are linked below. Individual experiments retain their own dates and additional sources in the report. A fingerprint identifies file bytes; completeness and tradability require separate checks.', '下列链接列出主要公开证据文件。各实验保留自己的日期，其他来源见专题报告。文件指纹用于核对版本，数据完整性与组合可交易性仍须分别核验。'],
  file: ['Selected public evidence files', '主要公开证据文件'],
} as const;
