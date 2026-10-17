import { expect, test } from '@playwright/test';

test('followup tables, chart, locale and downloads agree in light and dark modes', async ({page}) => {
  await page.goto('research/microcap/?lang=en-US');
  const section=page.locator('#microcap-followup');
  await expect(section.locator('table').first().locator('tbody tr')).toHaveCount(8);
  await expect(section).toContainText('688');
  const backfill=section.locator('section').filter({has:page.locator('#followup-backfill')});
  await expect(backfill).toContainText('619 / 619');
  await expect(backfill).toContainText('597 / 597');
  await expect(backfill).toContainText('5062');
  await expect(backfill).toContainText('5132');
  const projection=await (await page.request.get('data/microcap_action_backfill_review.json')).json();
  expect(projection.plans['90'].unqueried_names).toBe(0);
  expect(projection.plans['90'].events.blocked_event_count).toBe(82);
  expect(projection.raw_share_ready).toBe(false);
  await expect(section).toContainText('partial-window requests do not qualify');
  for(const theme of ['light','dark']) {
    await page.evaluate(value=>{document.documentElement.dataset.theme=value;},theme);
    const chart=section.locator('svg');
    expect(await chart.locator('rect').first().evaluate(el=>getComputedStyle(el).fill)).not.toBe('rgba(0, 0, 0, 0)');
    expect(await chart.locator('text.scenario').evaluateAll(nodes=>nodes.every(n=>{const b=(n as SVGGraphicsElement).getBBox();return b.x+b.width<585;}))).toBe(true);
  }
  await page.getByRole('button',{name:'Switch to Chinese'}).click();
  await expect(section).toContainText('全窗口查询证据');
  await expect(section).toContainText('真实股数');
  const md=await (await page.request.get('downloads/microcap-research.zh-CN.md')).text();
  expect(md).toContain('1.0.3');expect(md).toContain('688');expect(md).toContain('114');
  for(const locale of ['en-US','zh-CN']) {
    const svg=await page.request.get(`downloads/microcap-execution-followup.${locale}.svg`);
    expect(svg.status()).toBe(200);expect(await svg.text()).toContain('5.41%');
  }
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
