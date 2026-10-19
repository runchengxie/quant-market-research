import { useEffect, useRef, useState } from 'react';
import { overseasChartCopy as c } from '../content/overseas-chart-copy';
import { overseasCopy } from '../content/overseas-leadlag-copy';
import { costModels, costValue, selectCostRows, type CostRow } from '../lib/overseas-cost-chart';
import { readChartTheme } from '../theme';
import { baseChartOptions } from '../lib/chart-presentation';

export default function OverseasCostChart({ rows, svg }: { rows: CostRow[]; svg: string }) {
 const [locale, setLocale] = useState<0|1>(0);
 const [target, setTarget] = useState('510300');
 const [lag, setLag] = useState(0);
 const [revision, setRevision] = useState(0);
 const canvas = useRef<HTMLDivElement>(null);
 const chart = useRef<import('echarts').ECharts>();
 const t = (key: keyof typeof c) => c[key][locale];
 const modelName = (model: typeof costModels[number]) => overseasCopy.models[model][locale];
 const selected = selectCostRows(rows, target, lag);
 const updateSelection = (nextTarget: string, nextLag: number) => {
  setTarget(nextTarget); setLag(nextLag);
  try { sessionStorage.setItem('overseas-cost-selection', JSON.stringify({target: nextTarget, lag: nextLag})); } catch { /* Storage is optional. */ }
 };
 const sample = t(target === '510300' ? 'window510300' : 'window512480');
 useEffect(() => {
  try {
   const saved = JSON.parse(sessionStorage.getItem('overseas-cost-selection') ?? '{}');
   if (['510300','512480'].includes(saved.target) && [0,1].includes(saved.lag)) { setTarget(saved.target); setLag(saved.lag); }
  } catch { /* Tables remain available when storage is unavailable. */ }
  const sync = () => { setLocale(document.documentElement.lang === 'zh-CN' ? 1 : 0); setRevision(v => v + 1); };
  sync();
  const observer = new MutationObserver(sync);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['lang', 'data-theme'] });
  let disposed = false;
  let resize: ResizeObserver | undefined;
  import('./echarts').then(({echarts}) => {
   if (disposed || !canvas.current) return;
   chart.current = echarts.init(canvas.current);
   resize = new ResizeObserver(() => chart.current?.resize());
   resize.observe(canvas.current);
   setRevision(v => v + 1);
  });
  return () => { disposed = true; observer.disconnect(); resize?.disconnect(); chart.current?.dispose(); chart.current = undefined; };
 }, []);
 useEffect(() => {
  if (!chart.current) return;
  const theme = readChartTheme();
  const costs = [...new Set(selected.map(r => r.round_trip_bp!))];
  chart.current.setOption({
   ...baseChartOptions(theme, matchMedia('(prefers-reduced-motion: reduce)').matches),
   grid: { left: 12, right: 20, top: 80, bottom: 55, containLabel: true },
   legend: { type: 'scroll', top: 0, textStyle: { color: theme.label } },
   tooltip: { ...baseChartOptions(theme,true).tooltip, trigger: 'axis', confine: true, formatter: (params: any) => {
    const points = Array.isArray(params) ? params : [params];
    const cost = Number(points[0]?.axisValue);
    return [ `${t('cost')}: ${cost}`, sample, t(lag === 0 ? 'scheduled' : 'delayed'), ...points.map((p: any) => {
     const row = selected.find(r => r.model === p.seriesId && r.round_trip_bp === cost);
     return `${p.marker}${p.seriesName}: ${costValue(row?.mean_daily_net_bp) === null ? t('missing') : row!.mean_daily_net_bp!.toFixed(4)} bp · n=${row?.n ?? '—'}`;
    }) ].join('<br/>');
   } },
   xAxis: { type: 'category', data: costs, name: t('cost'), nameLocation: 'middle', nameGap: 32, axisLabel: { color: theme.label }, axisLine: { lineStyle: { color: theme.axis } } },
   yAxis: { type: 'value', name: t('axis'), axisLabel: { color: theme.label }, splitLine: { lineStyle: { color: theme.grid } } },
   series: costModels.map((model,i) => ({ id: model, name: modelName(model), type: 'line', connectNulls: false, symbolSize: 9, data: costs.map(cost => costValue(selected.find(r => r.model === model && r.round_trip_bp === cost)?.mean_daily_net_bp)), lineStyle: { color: ['#5276b8','#b77b42','#1d9d89','#a76c9f'][i] }, itemStyle: { color: ['#5276b8','#b77b42','#1d9d89','#a76c9f'][i] } })),
  }, true);
 }, [target,lag,locale,revision]);
 return <section data-overseas-cost-chart>
  <h3>{t('title')}</h3><p>{t('help')}</p>
  <div style={{display:'flex',flexWrap:'wrap',gap:'1rem'}}>
   <label>{t('etf')} <select aria-label={t('etf')} value={target} onChange={e=>updateSelection(e.target.value,lag)}><option>510300</option><option>512480</option></select></label>
   <label>{t('delay')} <select aria-label={t('delay')} value={lag} onChange={e=>updateSelection(target,Number(e.target.value))}><option value={0}>{t('scheduled')}</option><option value={1}>{t('delayed')}</option></select></label>
  </div>
  <p aria-live="polite" data-cost-sample>{sample} {t(lag === 0 ? 'scheduled' : 'delayed')}</p>
  <div ref={canvas} role="img" aria-label={`${t('title')}. ${t('mean')}. ${sample}`} style={{height:'380px',width:'100%'}} />
  <p>{t('mean')}. {t('caption')}</p>
  <a href={svg} download>{t('download')}</a>
  <details><summary>{t('table')}</summary><div style={{overflowX:'auto'}}><table><caption>{sample}</caption><thead><tr><th>{t('cost')}</th><th>{t('model')}</th><th>{t('mean')}</th><th>{t('n')}</th></tr></thead><tbody>{selected.map(r=><tr key={`${r.model}-${r.round_trip_bp}`}><td>{r.round_trip_bp}</td><th>{modelName(r.model as typeof costModels[number])}</th><td>{costValue(r.mean_daily_net_bp) === null ? t('missing') : r.mean_daily_net_bp!.toFixed(4)}</td><td>{r.n}</td></tr>)}</tbody></table></div></details>
 </section>;
}
