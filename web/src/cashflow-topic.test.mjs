import test from 'node:test';
import assert from 'node:assert/strict';
import { publicPages, pageForRoute } from './content/public-registry.ts';
import { legacyHashTarget, PUBLIC_ROUTES, withBase } from './lib/routes.ts';

test('cashflow keeps one main topic and a related replication report with the old recovery alias', () => {
  const topics = publicPages.filter(page => page.id === 'cashflow');
  const replication=publicPages.find(page=>page.id==='cashflow-replication');
  assert.equal(replication.route,'/research/cashflow/replication/');
  assert.ok(topics[0].related.includes(replication.id));
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
