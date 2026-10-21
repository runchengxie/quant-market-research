import { test, expect } from '@playwright/test';
for (const locale of ['en-US','zh-CN']) {
 test(`one valuation topic keeps evidence stages, reference sensitivities and forward limits: ${locale}`,async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto(`research/valuation-groups/?lang=${locale}`);
  await expect(page.getByTestId('valuation-directory')).toBeVisible();
  await expect(page.getByTestId('valuation-directory').locator('.valuation-stage-checked')).toHaveCount(2);
  await expect(page.getByTestId('round2-warning')).toContainText('39');
  await expect(page.getByTestId('round2-warning')).toContainText('revision_safe=false');
  await expect(page.getByTestId('round2-findings')).toContainText('-23.86');
  await expect(page.getByTestId('round2-findings')).toContainText('-6.39');
  await expect(page.getByTestId('round2-attribution-table').locator('tbody tr')).toHaveCount(5);
  await expect(page.getByTestId('round2-controls-table').locator('tbody tr')).toHaveCount(3);
  await page.getByTestId('round2-control-outcome').selectOption('strict');
  await expect(page.getByTestId('round2-controls-table').locator('tbody tr').last()).toContainText('16 / 36');
  await expect(page.getByTestId('round2-controls-table').locator('tbody tr').last().getByTestId('control-full-mean')).toHaveText(locale==='en-US'?'Unavailable':'不可用');
  await expect(page.getByTestId('round2-controls-table').locator('tbody tr').last().getByTestId('control-supported-mean')).not.toHaveText(locale==='en-US'?'Unavailable':'不可用');
  await page.getByTestId('round2-control-outcome').selectOption('reference_0');
  const table=page.getByTestId('round2-sensitivity-table');
  await expect(table.locator('tbody tr')).toHaveCount(5);
  await expect(table.locator('tbody tr').first()).toContainText('50.99%');
  await expect(table.locator('tbody tr').first()).toContainText('52.75%');
  await expect(table.locator('tbody tr').first()).toContainText('54.52%');
  await expect(table.locator('tbody tr').first()).toContainText(locale==='en-US'?'Unavailable':'不可用');
  await page.getByTestId('round2-scope').selectOption('B_all_remaining');
  await page.getByTestId('round2-metric').selectOption('pe_deducted_proxy');
  await page.getByTestId('round2-scenario').selectOption('close10');
  await expect(table.locator('tbody tr')).toHaveCount(5);
  await expect(page.getByTestId('round2-case-progress').locator('article')).toHaveCount(6);
  await expect(page.getByTestId('round2-case-progress')).not.toContainText(locale==='en-US'?'stays anonymous':'保持匿名');
  await expect(page.getByTestId('case-revision-warning')).toContainText('2024');
  await expect(page.getByTestId('case-revision-warning')).toContainText('revision_safe=false');
  await expect(page.getByTestId('case-pe_unresolved_reference')).toContainText('0.6647');
  await expect(page.getByTestId('case-pb_negative_gap')).toContainText(locale==='en-US'?'rather than a loss':'本身并未亏损');
  await expect(page.getByTestId('round2-case-progress').locator('a[href^="https://static.cninfo.com.cn/"]')).toHaveCount(16);
  await expect(page.getByTestId('round2-forward')).toContainText('12');
  await expect(page.getByTestId('round2-forward')).toContainText(locale==='en-US'?'has not started':'尚未开始');
  await expect(page.getByTestId('valuation-validation')).toContainText('2026-10-21T14:38:06');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.getByTestId('round2-metric').selectOption('pb_parent');
  await page.getByTestId('round2-scenario').selectOption('touch10');
  await page.getByTestId('round2-scope').selectOption('A_unpriced_only');
  if(process.env.STUDY_SCREENSHOTS) {
   await page.getByTestId('round2-findings').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-findings-mobile-${locale}.png`});
   await page.getByTestId('round2-controls').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-controls-mobile-${locale}.png`});
   await page.getByTestId('round2-case-progress').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-cases-mobile-${locale}.png`});
   await page.getByTestId('valuation-directory').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-directory-mobile-${locale}.png`});
   await page.locator('#valuation-round2').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-round2-mobile-${locale}.png`});
  }
 });
}
for (const locale of ['en-US','zh-CN']) test('desktop topic retains prior anchors and all original research links: '+locale,async({page})=>{
 await page.setViewportSize({width:1280,height:960});
 await page.goto(`research/valuation-groups/?lang=${locale}`);
 for(const id of ['valuation-annual','valuation-definitions','valuation-evidence','valuation-ledger','valuation-persistence','valuation-coverage-audit','valuation-cases','valuation-distributions']) await expect(page.locator('#'+id)).toHaveCount(1);
 await page.getByTestId('valuation-directory').locator('summary').click();
 for(const route of ['valuation-denominators-20261018','valuation-panel-20261018','financial-template-coverage-20261019','pb-roe','style-factors-18y']) await expect(page.getByTestId('valuation-directory').locator(`a[href*="${route}"]`)).toHaveAttribute('href',new RegExp('lang='+locale));
 if(process.env.STUDY_SCREENSHOTS) {
  await page.getByTestId('round2-findings').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-findings-desktop-${locale}.png`});
  await page.getByTestId('round2-controls').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-controls-desktop-${locale}.png`});
  await page.getByTestId('round2-case-progress').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-cases-desktop-${locale}.png`});
  await page.getByTestId('valuation-directory').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-directory-desktop-${locale}.png`});
  await page.locator('#valuation-round2').screenshot({style:'header, .skip-link { visibility: hidden !important; }',path:`${process.env.STUDY_SCREENSHOTS}/valuation-round2-desktop-${locale}.png`});
 }
});
