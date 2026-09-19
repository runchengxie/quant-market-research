import test from 'node:test';
import assert from 'node:assert/strict';
import { factorHref } from './lib/factor-links.ts';

test('factor links use known values and the Pages base once', () => {
  assert.equal(factorHref('/docs/research/factors/barra-factor-dictionary/', 'quality', '/quant-market-research'), '/quant-market-research/docs/research/factors/barra-factor-dictionary/?factor=quality');
  assert.match(factorHref('/research/style-factors-18y/', 'toString', '/'), /factor=size$/);
  assert.match(factorHref('/research/style-factors-18y/', '__proto__', '/'), /factor=size$/);
  assert.throws(() => factorHref('//evil.example/', 'size', '/'), /registered/);
});
