import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { liquidityCaveats, liquidityCaveatTranslations } from './liquidity-copy.ts';

const summary = JSON.parse(readFileSync(new URL('../public/data/liquidity/summary.json', import.meta.url), 'utf8'));

test('English liquidity caveats have complete translations and do not mutate source data', () => {
  for (const note of summary.caveats) assert.ok(liquidityCaveatTranslations[note], `missing English copy for caveat: ${note}`);
  const original = [...summary.caveats];
  const rendered = liquidityCaveats(summary.caveats, 'en-US');
  assert.doesNotMatch(rendered, /[\u3400-\u9fff]/);
  assert.deepEqual(summary.caveats, original);
});

test('Chinese liquidity explanations preserve the source data and its limits', () => {
  const original = [...summary.caveats];
  const rendered = liquidityCaveats(summary.caveats, 'zh-CN');
  assert.deepEqual(summary.caveats, original);
  assert.match(rendered, /Yahoo历史股数/);
  assert.match(rendered, /覆盖仍不完整/);
  assert.match(rendered, /2015年/);
  assert.match(rendered, /2020年/);
  assert.doesNotMatch(rendered, /；|不是.*而是/);
});
