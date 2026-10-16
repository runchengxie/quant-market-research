import { expect, test } from '@playwright/test';

test('reviewed comparison has one live locale, complete tables and reversible language switching', async ({ page }) => {
  await page.goto('research/microcap/?lang=en-US');
  const section=page.locator('#microcap-reviewed-comparison');
  const live=section.locator('[data-comparison-live]');
  await expect(live).toHaveAttribute('lang','en-US');
  await expect(section.locator('svg')).toHaveCount(1);
  await expect(section.locator('table')).toHaveCount(4);
  await expect(section.locator('svg circle')).toHaveCount(48);
  await expect(section.locator('tbody tr')).toHaveCount(192);
  await expect(live).not.toContainText('小盘');
  await live.locator('details').first().locator('summary').click();
  await expect(live.locator('details').first()).toHaveAttribute('open','');
  await page.getByRole('button',{name:'Switch to Chinese'}).click();
  await expect(live).toHaveAttribute('lang','zh-CN');
  await expect(live).toContainText('小盘');
  await expect(section.locator('svg')).toHaveCount(1);
  await expect(section.locator('svg')).toHaveAttribute('aria-labelledby',/zh-cn/);
  await expect(live.locator('a[download][href$=".svg"]')).toHaveAttribute('href',/microcap-exclusions.zh-CN.svg$/);
  await expect(section.locator('tbody tr')).toHaveCount(192);
  await page.getByRole('button',{name:'切换到英文'}).click();
  await expect(live).toHaveAttribute('lang','en-US');
  await expect(live).not.toContainText('小盘');
  await expect(section.locator('svg')).toHaveCount(1);
  const ids=await section.locator('[id]').evaluateAll(nodes=>nodes.map(node=>node.id));
  expect(new Set(ids).size).toBe(ids.length);
});

for(const locale of ['en-US','zh-CN']){
 test(`reviewed comparison honors ${locale} on initial load and dark mobile chart remains readable`,async({page})=>{
  await page.addInitScript(()=>localStorage.setItem('market-research-theme','dark'));
  await page.setViewportSize({width:390,height:844});
  await page.goto(`research/microcap/?lang=${locale}`);
  const section=page.locator('#microcap-reviewed-comparison'),live=section.locator('[data-comparison-live]');
  await expect(live).toHaveAttribute('lang',locale);
  await expect(page.locator('html')).toHaveAttribute('data-theme','dark');
  const svg=section.locator('svg');await expect(svg).toHaveCount(1);
  expect(await svg.locator('rect').first().evaluate(el=>getComputedStyle(el).fill)).not.toBe('rgb(255, 255, 255)');
  const contrast=await svg.evaluate(el=>{
   const luminance=(value:string)=>{const c=value.match(/[\d.]+/g)!.slice(0,3).map(Number).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return c[0]*.2126+c[1]*.7152+c[2]*.0722;};
   const background=luminance(getComputedStyle(el.querySelector('rect')!).fill);
   return Array.from(el.querySelectorAll('text')).map(node=>{const foreground=luminance(getComputedStyle(node).fill);return (Math.max(background,foreground)+.05)/(Math.min(background,foreground)+.05);});
  });
  expect(Math.min(...contrast)).toBeGreaterThanOrEqual(3);
  await expect(section.locator('svg circle')).toHaveCount(48);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  const download=live.locator('a[download][href$=".svg"]');
  const response=await page.request.get((await download.getAttribute('href'))!);expect(response.status()).toBe(200);expect(await response.text()).toContain(`microcap-exclusions-title-${locale.toLowerCase()}`);
 });
}
