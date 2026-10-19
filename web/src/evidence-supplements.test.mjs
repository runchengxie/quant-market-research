import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { publicDocs, publicPages } from './content/public-registry.ts';
import { englishCopy } from './content/locale-copy.ts';
import { resolveDocLink } from './content/rehype-public-docs.ts';

const entries = [
  ['microcap-st-exits', 'microcap-st-exit-evidence-20261019'],
  ['financial-template-coverage', 'financial-template-coverage-20261019'],
];
test('reviewed evidence supplements have bilingual routes, navigation and stable links', async () => {
  for (const [id, slug] of entries) {
    const en = publicDocs.find(doc => doc.id === id);
    const zh = publicDocs.find(doc => doc.id === `${id}-zh-CN`);
    assert.ok(en && zh);
    assert.ok(englishCopy(en).title.length > 0);
    assert.equal(resolveDocLink('docs/index.md', `research/experiments/${slug}.md`, '/quant-market-research'), `/quant-market-research/docs/research/experiments/${slug}/`);
    const body = await readFile(new URL(`../../docs/research/experiments/${slug}.md`, import.meta.url), 'utf8');
    assert.ok(body.includes(`${slug}.zh-CN.md`));
    assert.ok(!/\]\([^)]*\.json\)/.test(body.replace(/\]\(https?:[^)]*\)/g, '')));
  }
  assert.ok(publicPages.find(page => page.id === 'microcap').related.includes('microcap-st-exits'));
  assert.ok(publicPages.find(page => page.id === 'pb-roe').related.includes('financial-template-coverage'));
});

test('financial diagnosis is a separate exact reviewed aggregate without replacing the baseline', async () => {
  const source = await readFile(new URL('../../docs/research/experiments/financial-template-coverage-20261019.json', import.meta.url), 'utf8');
  const published = await readFile(new URL('../public/data/financial_template_coverage_reviewed.json', import.meta.url), 'utf8');
  assert.equal(published, source);
  const data = JSON.parse(published);
  assert.equal(data.schema_version, 'financial_template_coverage_review.v1');
  assert.equal(data.historical_pit_certified, false);
  assert.equal(data.returns_backtested, false);
  assert.equal(data.published_owner_asset, false);
  assert.equal(data.comparison.all_quotes.before.common_five, 1743);
  assert.equal(data.comparison.all_quotes.after.common_five, 1794);
  const baseline = JSON.parse(await readFile(new URL('../public/data/valuation_panel_reviewed.json', import.meta.url), 'utf8'));
  assert.notEqual(baseline.schema_version, data.schema_version);
});
