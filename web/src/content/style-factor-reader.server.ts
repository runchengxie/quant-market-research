import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

/** Validate and project the immutable reviewed archive; returns remain in percent. */
export function buildStyleFactorReader(summaryRaw: string, yearlyRaw: string) {
  const summary = JSON.parse(summaryRaw);
  if (!Array.isArray(summary) || summary.length !== 19) throw new Error('expected 19 historical factors');
  const ids: string[] = summary.map(row => row.factor);
  if (ids.some(id => typeof id !== 'string' || !id) || new Set(ids).size !== ids.length) throw new Error('invalid factor IDs');
  type Annual = { year: number; periodStart: string; periodEnd: string; days: number; partial: boolean; value: number };
  const annual = new Map<string, Annual[]>(ids.map(id => [id, []]));
  const [header, ...lines] = yearlyRaw.trim().split(/\r?\n/);
  const columns = header.split(',');
  const expected = ['year', 'factor', 'days', 'period_start', 'period_end', 'is_partial_year', 'period_return'];
  if (expected.some(key => !columns.includes(key)) || new Set(columns).size !== columns.length) throw new Error('invalid yearly header');
  const dates: string[] = [];
  for (const line of lines) {
    const cells = line.split(',');
    if (cells.length !== columns.length) throw new Error('invalid yearly row');
    const row = Object.fromEntries(columns.map((key, i) => [key, cells[i]]));
    const year = Number(row.year), days = Number(row.days), value = Number(row.period_return);
    const validDate = (date: string) => /^\d{4}-\d{2}-\d{2}$/.test(date) && Number.isFinite(Date.parse(date)) && new Date(date).toISOString().slice(0, 10) === date && Number(date.slice(0, 4)) === year;
    if (!annual.has(row.factor) || !Number.isInteger(year) || !Number.isInteger(days) || days <= 0 || !row.period_return.trim() || !Number.isFinite(value) || !validDate(row.period_start) || !validDate(row.period_end) || row.period_start > row.period_end || !['True', 'False'].includes(row.is_partial_year)) throw new Error('invalid yearly observation');
    const values = annual.get(row.factor)!;
    if (values.some(item => item.year === year)) throw new Error('duplicate factor/year');
    values.push({ year, periodStart: row.period_start, periodEnd: row.period_end, days, partial: row.is_partial_year === 'True', value });
    dates.push(row.period_start, row.period_end);
  }
  if (!dates.length || [...annual.values()].some(values => !values.length)) throw new Error('missing factor observations');
  dates.sort();
  const hash = (raw: string) => createHash('sha256').update(raw).digest('hex');
  return { schemaVersion: 1, evidenceStage: 'historical_archive', unit: 'percent', coverageStart: dates[0], coverageEnd: dates.at(-1), sourceHashes: { summary: hash(summaryRaw), yearly: hash(yearlyRaw) }, factors: ids.map(id => ({ id, annual: annual.get(id)!.sort((a, b) => a.year - b.year) })) };
}
export async function readStyleFactorReader(root = process.cwd()) {
  const [summary, yearly] = await Promise.all([
    readFile(resolve(root, 'public/data/barra/historical_factor_summary.json'), 'utf8'),
    readFile(resolve(root, 'public/data/barra/factor_yearly.csv'), 'utf8'),
  ]);
  return buildStyleFactorReader(summary, yearly);
}
