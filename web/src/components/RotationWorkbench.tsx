import { useState } from 'react';
import { ResearchBarChart } from './ResearchCharts';
import { englishLocale, SortableTable } from './react/research-shared';
import { experimentCards, groupLabels, groupNotes, selectWeeklyRows, type Copy, type Group } from '../content/rotation-research';
const text = (value: Copy) => value[englishLocale() ? 0 : 1];
const ui = (en: string, zh: string) => text([en, zh]);
const pct = (value: number) => `${value.toFixed(2)}%`;
export function ExperimentExplorer() {
  const [family, setFamily] = useState('all');
  const cards = experimentCards.filter(card => family === 'all' || card.family === family);
  return <section className="panel" id="experiments" aria-labelledby="experiment-heading">
    <h2 id="experiment-heading">{ui('Explore the research branches', '探索研究分支')}</h2>
    <label className="rotation-control">{ui('Research branch', '研究分支')} <select aria-label={ui('Research branch', '研究分支')} value={family} onChange={event => setFamily(event.target.value)}>
      <option value="all">{ui('All branches', '全部分支')}</option><option value="etf">{ui('ETF selection and allocation', 'ETF 选择与配置')}</option><option value="hotspot">{ui('Hotspot stock evidence', '热点个股证据')}</option><option value="bridge">{ui('Theme-to-ETF validation gap', '主题到 ETF 的验证缺口')}</option>
    </select></label>
    <p role="status">{ui(`${cards.length} research branches shown`, `显示 ${cards.length} 项研究分支`)}</p>
    <div className="rotation-card-grid">{cards.map(card => <article className="rotation-card" key={card.title[0]}>
      <span className="section-kicker">{ui(card.family === 'bridge' ? 'Research proposal' : 'Historical diagnostic', card.family === 'bridge' ? '研究设想' : '历史诊断')}</span>
      <h3>{text(card.title)}</h3><p>{text(card.observation)}</p><p className="panel-note">{text(card.scope)}</p>
      <details><summary>{ui('What remains to test', '还要检验什么')}</summary><p>{text(card.next)}</p></details>
      <a href={`#${card.anchor}`}>{ui('Read evidence and limitations →', '查看证据与限制 →')}</a>
    </article>)}</div>
  </section>;
}
export function WeeklyExperimentCharts() {
  const [group, setGroup] = useState<Group>('risk');
  const [measure, setMeasure] = useState<'cagr' | 'sharpe' | 'drawdown'>('drawdown');
  const rows = selectWeeklyRows(group);
  const metricLabels = { cagr: ui('Annualized return', '年化收益'), sharpe: ui('Sharpe ratio', '夏普比率'), drawdown: ui('Maximum drawdown', '最大回撤') };
  const format = (value: number) => measure === 'sharpe' ? value.toFixed(3) : pct(value);
  return <section className="panel" aria-labelledby="weekly-chart-title">
    <h3 id="weekly-chart-title">{ui('Compare one experiment family at a time', '每次比较一组实验')}</h3>
    <div className="rotation-controls"><label className="rotation-control">{ui('Experiment group', '实验分组')} <select aria-label={ui('Experiment group', '实验分组')} value={group} onChange={event => setGroup(event.target.value as Group)}>
      {(Object.keys(groupLabels) as Group[]).map(key => <option value={key} key={key}>{text(groupLabels[key])}</option>)}
    </select></label>
    <label className="rotation-control">{ui('Chart measure', '图表指标')} <select aria-label={ui('Chart measure', '图表指标')} value={measure} onChange={event => setMeasure(event.target.value as typeof measure)}>
      {Object.entries(metricLabels).map(([key, label]) => <option value={key} key={key}>{label}</option>)}
    </select></label></div>
    <p role="status">{text(groupLabels[group])} · {metricLabels[measure]} · {rows.length} {ui('configurations', '组配置')}</p>
    <ResearchBarChart rows={rows.map(row => ({ name: text(row.label), value: String(row[measure]) }))} labelKey="name" valueKey="value" formatter={format} />
    <p className="panel-note">{text(groupNotes[group])}</p>
    <details open className="chart-data"><summary>{ui('Inspect and sort all metrics', '查看并排序全部指标')}</summary>
      <SortableTable key={group} rows={rows.map(row => ({ name: text(row.label), cagr: row.cagr.toFixed(2), sharpe: row.sharpe.toFixed(3), drawdown: row.drawdown.toFixed(2), fallback: row.fallback == null ? '' : row.fallback.toFixed(2), executions: row.executions == null ? ui('Not reported', '未提供') : String(row.executions) }))} columns={[
        ['name', ui('Configuration', '配置')], ['cagr', `${metricLabels.cagr} (%)`], ['sharpe', metricLabels.sharpe], ['drawdown', `${metricLabels.drawdown} (%)`], ['fallback', ui('Average bond fallback weight (%)', '平均债券配置（%）')], ['executions', ui('Executed rebalances', '执行调仓次数')],
      ]} />
    </details>
    <p className="panel-note">{ui('Missing cells mean the source note did not report that measure. They are not zeros. Maximum drawdown is a loss: a value closer to zero indicates a shallower decline. Use the table headers to sort; chart legends in the ETF charts can hide or restore a series.', '缺失单元格表示原记录未提供该指标，不是零。最大回撤表示损失，越接近零代表跌幅越浅。点击表头可排序；ETF 图表的图例可隐藏或恢复曲线。')}</p>
  </section>;
}
