import test from 'node:test';
import assert from 'node:assert/strict';
import { publicPages, pageForRoute } from './content/public-registry.ts';
import { legacyHashTarget, PUBLIC_ROUTES, withBase } from './lib/routes.ts';

test('cashflow is a single searchable topic with both evidence sets and the old route as an alias', () => {
  const topics = publicPages.filter(page => page.section === 'research' && page.topic === 'cashflow');
  assert.equal(topics.length, 1);
  assert.equal(topics[0].title, '现金流指数研究');
  assert.deepEqual(topics[0].snapshotKeys, ['cashflow.performance', 'cashflow.recovery']);
  assert.equal(pageForRoute('/research/cashflow/recovery/'), topics[0]);
  for (const id of ['indices', 'microcap']) {
    const independent = publicPages.find(page => page.id === id);
    assert.ok(independent && independent.topic !== 'cashflow');
    assert.ok(independent.related.includes('cashflow'));
    assert.ok(topics[0].related.includes(id));
  }
});

test('recovery links go directly to the canonical topic anchor under root and Pages bases', () => {
  for (const base of ['/', '/quant-market-research/']) {
    const expected = `${base}research/cashflow/#cashflow-recovery`;
    assert.equal(withBase(PUBLIC_ROUTES.cashflowRecovery, base), expected);
    assert.equal(legacyHashTarget('#cashflow-recovery', base), expected);
  }
});
