import { test } from 'node:test';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { buildStyleFactorReader, readStyleFactorReader } from './content/style-factor-reader.server.ts';

test('reader retains all archive IDs and exact percent period returns', async () => {
 const reader = await readStyleFactorReader();
 assert.equal(reader.factors.length, 19);
 const summaryRaw = await readFile('public/data/barra/historical_factor_summary.json', 'utf8');
 const yearlyRaw = await readFile('public/data/barra/factor_yearly.csv', 'utf8');
 assert.deepEqual(reader.factors.map(f => f.id), JSON.parse(summaryRaw).map(f => f.factor));
 assert.equal(reader.sourceHashes.summary, createHash('sha256').update(summaryRaw).digest('hex'));
 assert.equal(reader.sourceHashes.yearly, createHash('sha256').update(yearlyRaw).digest('hex'));
 const [header, ...rows] = yearlyRaw.trim().split(/\r?\n/).map(line => line.split(','));
 for (const cells of rows) {
  const row = Object.fromEntries(header.map((key, i) => [key, cells[i]]));
  const observation = reader.factors.find(f => f.id === row.factor).annual.find(a => a.year === Number(row.year));
  assert.equal(observation.value, Number(row.period_return));
 }
 assert.equal(reader.factors.reduce((count, factor) => count + factor.annual.length, 0), rows.length);
 assert.equal(reader.unit, 'percent');
 assert.equal(reader.evidenceStage, 'historical_archive');
 assert.match(reader.sourceHashes.yearly, /^[a-f0-9]{64}$/);
 const beta = reader.factors.find(f => f.id === 'beta');
 assert.deepEqual(beta.annual[0], { year: 2008, periodStart: '2008-08-01', periodEnd: '2008-12-31', days: 103, partial: true, value: 4.54 });
 for (const factor of reader.factors) assert.deepEqual(factor.annual.map(a => a.year), factor.annual.map(a => a.year).sort((a,b) => a-b));
});
test('reader rejects duplicate, invalid, and cross-year rows', async () => {
 const summary = await readFile('public/data/barra/historical_factor_summary.json', 'utf8');
 const yearly = await readFile('public/data/barra/factor_yearly.csv', 'utf8');
 const row = yearly.trim().split('\n')[1];
 for (const bad of [yearly.trim()+'\n'+row, yearly.replace('2008-08-01','2009-08-01'), yearly.replace(',103,',',0,'), yearly.replace(',4.54,',',NaN,')]) assert.throws(() => buildStyleFactorReader(summary, bad));
});
