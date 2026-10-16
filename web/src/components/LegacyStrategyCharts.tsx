import { useState } from 'react';
import { ResearchBarChart, ResearchLineChart } from './ResearchCharts';
import { SimpleTable, englishLocale } from './react/research-shared';

type EtfRow = { costBps: number; raw: Record<string, number>; adjusted: Record<string, number> };
type EtfDisplayRow = { cost: string; [key: string]: string | number };
type AnnualRow = { year: number; regression: number; basket: number };
type HotspotRow = { costBps: number; meanUpliftPp: number; positiveEvents: number; eventCount: number };

const ui = (zh: string, en: string) => englishLocale() ? en : zh;
const recipeLabels: Record<string, [string, string]> = {
  linear_rank: ['线性排序', 'Linear rank'], lightgbm_regression: ['LightGBM 回归', 'LightGBM regression'],
  lightgbm_ranker: ['LightGBM 排序', 'LightGBM ranker'], fixed_share_basket: ['固定份额篮子', 'Fixed-share basket'],
  single_etf_baseline: ['单只 ETF 基准', 'Single ETF baseline'],
};
const percent = (value: number) => `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;

export function EtfSensitivityCharts({ rows, annual }: { rows: EtfRow[]; annual: AnnualRow[] }) {
  const [valuation, setValuation] = useState<'raw' | 'adjusted'>('adjusted');
  const selected: EtfDisplayRow[] = rows.map(row => ({ ...row[valuation], cost: `${row.costBps} bps` }));
  const recipes = Object.keys(recipeLabels) as Array<keyof typeof recipeLabels>;
  const yearly = annual.map(row => ({ year: String(row.year), regression: row.regression / 100, basket: row.basket / 100 }));
  const series = recipes.map((recipe, index) => ({
    name: ui(...recipeLabels[recipe]), values: selected.map(row => Number(row[recipe]) / 100),
    color: ['#a14e42', '#317c72', '#7257a5', '#2863a5', '#a8752a'][index],
  }));
  return <div className="legacy-chart-stack">
    <section className="panel" aria-labelledby="etf-cost-chart-title">
      <div className="panel-title"><h2 id="etf-cost-chart-title">{ui('成本与价格口径会怎样改变结果？', 'How do costs and price conventions change results?')}</h2><span className="tag warm">{ui('累计收益', 'Cumulative return')}</span></div>
      <label className="legacy-chart-control">{ui('价格口径', 'Price convention')}
        <select aria-label={ui('价格口径', 'Price convention')} value={valuation} onChange={event => setValuation(event.target.value as 'raw' | 'adjusted')}>
          <option value="adjusted">{ui('同日因子复权', 'Same-day factor-adjusted')}</option><option value="raw">{ui('原始价格', 'Raw prices')}</option>
        </select>
      </label>
      <ResearchLineChart labels={selected.map(row => row.cost)} series={series} />
      <p className="panel-note">{ui('每条线代表一个模型或基准，横轴是单边成本假设。切换价格口径后，图表和表格同步更新。复权口径只是估值敏感性，不是券商现金流账本。', 'Each line is a model or baseline; the x-axis shows assumed one-way costs. The chart and table update together when you change the price convention. Adjusted prices are a valuation sensitivity, not a broker cash-flow ledger.')}</p>
      <details className="chart-data" open><summary>{ui('查看图表数值', 'View chart values')}</summary>
        <SimpleTable rows={selected.map(row => ({ cost: row.cost, ...Object.fromEntries(recipes.map(recipe => [ui(...recipeLabels[recipe]), percent(Number(row[recipe]))])) }))} columns={[["cost", ui('单边成本', 'One-way cost')], ...recipes.map(recipe => [ui(...recipeLabels[recipe]), ui(...recipeLabels[recipe])])]} />
      </details>
    </section>
    <section className="panel" aria-labelledby="etf-year-chart-title">
      <div className="panel-title"><h2 id="etf-year-chart-title">{ui('回归模型的收益集中在哪些年份？', 'Which years account for the regression recipe’s returns?')}</h2></div>
      <ResearchLineChart labels={yearly.map(row => row.year)} series={[
        { name: ui('LightGBM 回归', 'LightGBM regression'), values: yearly.map(row => row.regression), color: '#317c72' },
        { name: ui('固定份额篮子', 'Fixed-share basket'), values: yearly.map(row => row.basket), color: '#2863a5' },
      ]} />
      <p className="panel-note">{ui('按退出年份汇总，复权价格、25 基点成本。2021 年只有 2 月 18 日起的部分年度。年度切片是在完整区间结果已知后查看，属于探索性描述。', 'Grouped by exit year using adjusted prices and 25 bps cost. 2021 is partial and starts on February 18. These annual slices were examined after the full-window result was known, so they are exploratory descriptions.')}</p>
      <SimpleTable rows={annual.map(row => ({ year: String(row.year), regression: percent(row.regression), basket: percent(row.basket) }))} columns={[["year", ui('年份', 'Year')], ["regression", ui('回归模型', 'Regression')], ["basket", ui('固定篮子', 'Fixed basket')]]} />
    </section>
  </div>;
}

export function HotspotSensitivityChart({ rows }: { rows: HotspotRow[] }) {
  const [measure, setMeasure] = useState<'uplift' | 'positive'>('uplift');
  const chartRows = rows.map(row => ({ cost: `${row.costBps} bps`, value: measure === 'uplift' ? row.meanUpliftPp : row.positiveEvents }));
  const tableRows = rows.map(row => ({
    cost: `${row.costBps} bps`, uplift: `${row.meanUpliftPp.toFixed(3)} pp`,
    positive: `${row.positiveEvents} / ${row.eventCount}`,
  }));
  return <section className="panel" aria-labelledby="hotspot-sensitivity-title">
    <div className="panel-title"><h2 id="hotspot-sensitivity-title">{ui('成本变化后，热点叠加还有多少增量？', 'How much uplift remains after costs?')}</h2></div>
    <label className="legacy-chart-control">{ui('显示指标', 'Show measure')}
      <select aria-label={ui('显示指标', 'Show measure')} value={measure} onChange={event => setMeasure(event.target.value as 'uplift' | 'positive')}>
        <option value="uplift">{ui('平均配对增量（百分点）', 'Mean paired uplift (pp)')}</option>
        <option value="positive">{ui('正向事件数', 'Positive events')}</option>
      </select>
    </label>
    <ResearchBarChart rows={chartRows.map(row => ({ cost: row.cost, value: String(row.value) }))} labelKey="cost" valueKey="value" color="#317c72" formatter={value => measure === 'uplift' ? `${value.toFixed(3)} pp` : `${value.toFixed(0)} / 4`} />
    <p className="panel-note">{ui('均值是四个独立五日事件的等权平均增量；正向事件数表示叠加组收益高于未叠加组的事件个数。两项指标单位不同，因此用上方菜单切换。', 'The mean is the equal-weight average paired uplift across four isolated five-session events. Positive-event count records how often the overlay arm outperformed its paired no-overlay arm. The measures use different units, so choose one above.')}</p>
    <SimpleTable rows={tableRows} columns={[["cost", ui('单边成本', 'One-way cost')], ["uplift", ui('平均增量', 'Mean uplift')], ["positive", ui('正向事件', 'Positive events')]]} />
  </section>;
}
