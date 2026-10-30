import { expect, test } from '@playwright/test';

test('canonical market-style reader exposes archived percent observations', async ({ request }) => {
  const response = await request.get('data/style-factors/reader.json');
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.schemaVersion).toBe(1);
  expect(data.evidenceStage).toBe('historical_archive');
  expect(data.unit).toBe('percent');
  expect(data.factors).toHaveLength(19);
  expect(data.sourceHashes.yearly).toMatch(/^[a-f0-9]{64}$/);
  expect(data.factors.find((factor: any) => factor.id === 'beta').annual[0]).toEqual({ year: 2008, periodStart: '2008-08-01', periodEnd: '2008-12-31', days: 103, partial: true, value: 4.54 });
});
