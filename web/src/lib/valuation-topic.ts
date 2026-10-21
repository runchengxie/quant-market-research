export type ValuationDistribution = {
  formation_date: string; group: string; metric: string; sample_basis: string;
  minimum: number | null; p01: number | null; p05: number | null;
  valid_n: number; total_n: number; nonpositive_denominator_n: number; missing_or_invalid_n: number;
};
export type AnnualValuation = ValuationDistribution & {
  year: string; sampled_minimum: number | null; sampled_dates: string[]; sampled_valid_n: number[];
};

export function annualValuations(rows: ValuationDistribution[], group: string, metric: string): AnnualValuation[] {
  const selected = rows.filter(r => r.group === group && r.metric === metric && r.sample_basis === 'metric_available')
    .sort((a, b) => a.formation_date.localeCompare(b.formation_date));
  if (new Set(selected.map(r => r.formation_date)).size !== selected.length) throw new Error('duplicate annual observation');
  const years = [...new Set(selected.map(r => r.formation_date.slice(0, 4)))];
  return years.map(year => {
    const observations = selected.filter(r => r.formation_date.startsWith(year));
    const last = observations.at(-1)!;
    const positive = observations.filter(r => r.minimum != null && Number.isFinite(r.minimum) && r.minimum > 0);
    const sampled = positive.length ? Math.min(...positive.map(r => r.minimum!)) : null;
    const ties = positive.filter(r => r.minimum === sampled);
    return { ...last, year, sampled_minimum: sampled, sampled_dates: ties.map(r => r.formation_date), sampled_valid_n: ties.map(r => r.valid_n) };
  });
}

export function positiveSegments<T extends { formation_date: string }>(rows: T[], key: keyof T) {
  const segments: { index: number; value: number }[][] = [];
  let current: { index: number; value: number }[] = [];
  rows.forEach((r, index) => {
    const value = r[key];
    const adjacent = !index || Number(r.formation_date.slice(0, 4)) === Number(rows[index - 1].formation_date.slice(0, 4)) + 1;
    if (!adjacent || typeof value !== 'number' || !Number.isFinite(value) || value <= 0) {
      if (current.length) segments.push(current);
      current = [];
    }
    if (typeof value === 'number' && Number.isFinite(value) && value > 0) current.push({ index, value });
  });
  if (current.length) segments.push(current);
  return segments;
}

type RankPair = { first: string; second: string; n: number; spearman: number; bottom_quintile_jaccard: number };
type Panel = { monthly?: { date: string; quote_records: number; common_five: number; metrics: { metric: string; available: number }[]; rank_pairs: RankPair[] }[] };
type Legacy = { factor: string; days: number; geometric_annual_ret: number; max_drawdown: number };
type Manifest = { historical_source?: string; historical_integrity?: { checked_receipts: number; matching_receipts: number; mismatch: string; exact_generating_revision_recovered: boolean } };
type GapAudit = { exclusive_reasons: { metric: string; reason: string; n: number }[]; basket_support: { metric: string; quintile: number; attempted_months: number; minimum_unresolved_members: number; complete_months: number }[] };

export function buildTopicEvidence(panel: Panel, factors: Legacy[], manifest: Manifest, audit: GapAudit) {
  const first = panel.monthly?.[0];
  const latest = panel.monthly?.at(-1);
  if (!first || !latest || manifest.historical_source !== 'style-factors/weekly-20260904') throw new Error('unexpected source version or coverage snapshot');
  const early = first.metrics.find(r => r.metric === 'pe_ttm');
  if (!early || first.date !== '20160129' || latest.date !== '20261016') throw new Error('unexpected coverage snapshot');
  const historical = ['value', 'earnings_yield', 'ps_value'].map(id => {
    const row = factors.find(r => r.factor === id);
    if (!row || row.days !== 4518 || !Number.isFinite(row.geometric_annual_ret)) throw new Error('unexpected historical source summary');
    return { factor: id, days: row.days, geometric_annual_ret: row.geometric_annual_ret, max_drawdown: row.max_drawdown };
  });
  const gaps = ['pb_parent', 'pe_deducted_proxy'].map(metric => {
    const rows = audit.exclusive_reasons.filter(r => r.metric === metric);
    const resolved = rows.find(r => r.reason === 'resolved')?.n;
    const reasons = rows.filter(r => r.reason !== 'resolved').map(r => ({ reason: r.reason, count: r.n }));
    const unresolved = reasons.reduce((sum, r) => sum + r.count, 0);
    const baskets = audit.basket_support.filter(r => r.metric === metric).sort((a, b) => a.quintile - b.quintile);
    const expected = metric === 'pb_parent' ? [185237, 4560] : [131115, 2160];
    if (resolved !== expected[0] || unresolved !== expected[1] || baskets.length !== 5 || baskets.some(b => b.attempted_months !== 36 || b.complete_months !== 0)) throw new Error('gap totals do not match the audited snapshot');
    return { group: 'all_market' as const, metric, resolved, unresolved, total: resolved + unresolved, reasons,
      minimum_missing_by_quintile: baskets.map(b => b.minimum_unresolved_members) };
  });
  return { schema_version: 'low_valuation_topic.v1', evidence_status: 'unpublished_retrospective_draft',
    early_coverage: { date: first.date, available: early.available, quoted: first.quote_records },
    ranking: { date: latest.date, common_n: latest.common_five, quoted_n: latest.quote_records,
      pairs: latest.rank_pairs.map(r => ({ first: r.first, second: r.second, n: r.n, spearman: r.spearman, bottom_quintile_jaccard: r.bottom_quintile_jaccard })) },
    legacy: { source: manifest.historical_source, start: '20080201', end: '20260904', days: 4518,
      missing_holding_return: 'zero', integrity: manifest.historical_integrity, factors: historical }, gaps };
}
export type TopicEvidence = ReturnType<typeof buildTopicEvidence>;
