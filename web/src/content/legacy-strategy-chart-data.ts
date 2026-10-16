type Metric = { name: string; unit: string; value: number };
type Study = { id: string; metrics: Metric[] };

const metricValue = (study: Study, name: string, unit: string) => {
  const metric = study.metrics.find(row => row.name === name && row.unit === unit);
  if (!metric || !Number.isFinite(metric.value)) throw new Error(`Reviewed chart metric missing: ${name}`);
  return metric.value;
};

export function etfSensitivityRows(study: Study) {
  if (study.id !== 'etf-rotation') throw new Error('Unexpected study for ETF chart');
  const recipes = ['linear_rank', 'lightgbm_regression', 'lightgbm_ranker', 'fixed_share_basket', 'single_etf_baseline'] as const;
  return [0, 10, 25, 50].map(costBps => {
    const values = (valuation: 'raw' | 'factor_adjusted') => Object.fromEntries(recipes.map(recipe => [
      recipe,
      metricValue(study, `etf.cumulative_return.${valuation}.${recipe}.cost_${costBps}_bps`, 'percent'),
    ])) as Record<(typeof recipes)[number], number>;
    return { costBps, raw: values('raw'), adjusted: values('factor_adjusted') };
  });
}

export function etfAnnualRows(study: Study) {
  if (study.id !== 'etf-rotation') throw new Error('Unexpected study for ETF chart');
  return [2021, 2022, 2023, 2024, 2025].map(year => ({
    year,
    regression: metricValue(study, `etf.calendar_return.factor_adjusted.lightgbm_regression.year_${year}.cost_25_bps`, 'percent'),
    basket: metricValue(study, `etf.calendar_return.factor_adjusted.fixed_share_basket.year_${year}.cost_25_bps`, 'percent'),
  }));
}

export function hotspotSensitivityRows(study: Study) {
  if (study.id !== 'hotsector') throw new Error('Unexpected study for hotspot chart');
  return [0, 25, 50].map(costBps => ({
    costBps,
    meanUpliftPp: metricValue(study, `hotspot.mean_event_delta.cost_${costBps}_bps`, 'percentage_points'),
    positiveEvents: metricValue(study, `hotspot.positive_event_count.cost_${costBps}_bps`, 'events'),
    eventCount: 4,
  }));
}
