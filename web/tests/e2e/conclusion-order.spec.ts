import { expect, test } from '@playwright/test';

test('conclusion and evidence boundary precede cash-flow charts and methods', async ({ page }) => {
  await page.goto('research/cashflow/');
  const verdict = page.locator('.research-verdict');
  await expect(verdict.getByRole('heading', { name: 'Current conclusion' })).toBeVisible();
  await expect(verdict).toContainText('Replication under review');
  expect(await verdict.evaluate(el => Boolean(el.compareDocumentPosition(document.querySelector('#topic-content')!) & Node.DOCUMENT_POSITION_FOLLOWING))).toBe(true);
  expect(await page.locator('#topic-content').evaluate(el => Boolean(el.compareDocumentPosition(document.querySelector('#research-method')!) & Node.DOCUMENT_POSITION_FOLLOWING))).toBe(true);
  await page.getByRole('button', { name: 'Switch to Chinese', exact: true }).click();
  await expect(verdict.getByRole('heading', { name: '当前结论' })).toBeVisible();
  await expect(verdict).toContainText('证据边界');
});
