import type { LiquidityPeriodMarket, LiquiditySummary } from '../components/react/research-shared';

export type LiquidityMetric = 'median_usd' | 'mean_usd' | 'p90_usd';
export type LiquidityIssue = { code: 'total_count_mismatch' | 'sub100m_count_mismatch'; reported: number; grouped: number };

export function auditLiquidityMarket(market: LiquidityPeriodMarket): LiquidityIssue[] {
  const issues: LiquidityIssue[] = [];
  const counts = market.buckets.map(bucket => bucket.count);
  if (counts.length && counts.every(count => Number.isInteger(count) && count! >= 0)) {
    const total = counts.reduce<number>((sum, count) => sum + count!, 0);
    if (market.eligible_stocks != null && total !== market.eligible_stocks)
      issues.push({code: 'total_count_mismatch', reported: market.eligible_stocks, grouped: total});
    // This contract's first two buckets are < $10m and $10m-$100m.
    if (market.buckets[0]?.label === '< $10m' && market.buckets[1]?.label === '$10m-$100m' && market.sub_100m_count != null) {
      const small = counts[0]! + counts[1]!;
      if (small !== market.sub_100m_count) issues.push({code: 'sub100m_count_mismatch', reported: market.sub_100m_count, grouped: small});
    }
  }
  return issues;
}

export function marketsForPeriod(summary: LiquiditySummary, period: string): LiquidityPeriodMarket[] {
  if (period === 'latest') return summary.markets;
  const selected = summary.periods?.find(item => item.period === period);
  return !selected || selected.status === 'pending' ? [] : selected.markets;
}

export function liquidityComparison(markets: LiquidityPeriodMarket[], bucket: number, metric: LiquidityMetric) {
  const label = markets[0]?.buckets[bucket]?.label;
  return markets.filter(market => !auditLiquidityMarket(market).length && market.status !== 'incomplete')
    .map(market => {
      const selected = market.buckets.find(item => item.label === label);
      const value = selected?.[metric];
      return {market: market.market, value: typeof value === 'number' && Number.isFinite(value) ? value : null};
    });
}

/** Arithmetic order budget only; no claim of fills, impact, or portfolio capacity. */
export function mechanicalOrderBudget(turnover: number | null, participation: number, days: number): number | null {
  if (!Number.isFinite(participation) || participation <= 0 || participation > 1 || !Number.isInteger(days) || days <= 0)
    throw new RangeError('Participation must be in (0, 1] and days a positive integer');
  if (turnover == null) return null;
  if (!Number.isFinite(turnover) || turnover < 0) throw new RangeError('Turnover must be finite and nonnegative');
  const result = turnover * participation * days;
  if (!Number.isFinite(result)) throw new RangeError('Order budget exceeds the finite numeric range');
  return result;
}
