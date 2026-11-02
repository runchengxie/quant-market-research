import{test,expect}from'@playwright/test';
const topics=['returns','allocation','implementation'];
for(const width of[320,1280])for(const locale of['en-US','zh-CN'])test(`full evidence directory and dated version at ${width} ${locale}`,async({page})=>{
 await page.setViewportSize({width,height:900});
 for(const topic of topics){await page.goto(`research/asset-${topic}/?lang=${locale}`);const links=page.locator('.asset-page-contents a');expect(await links.count()).toBeGreaterThan(topic==='returns'?5:topic==='allocation'?3:2);
  const ids=await links.evaluateAll(xs=>xs.map(x=>(x as HTMLAnchorElement).hash.slice(1)));const status=await page.evaluate(ids=>ids.map(id=>({id,count:document.querySelectorAll(`[id="${id}"]`).length,open:!document.getElementById(id)?.closest('details:not([open])')})),ids);expect(status.filter(x=>x.count!==1||!x.open)).toEqual([]);
  await expect(page.locator('[data-evidence-version-date]').first()).toHaveText('2026-11-01');await expect(page.locator('#asset-evidence-version')).toContainText(locale==='zh-CN'?'北京时间':'Beijing time');await expect(page.locator('#asset-evidence-version a[data-version-manifest]')).toHaveAttribute('href',/\/dc85d825d4e3eadd587020ffced36e038c0df27f\/studies\/asset_returns\/release-manifest.json$/);
  await expect(page.locator('body')).toHaveJSProperty('scrollWidth',width);
 }
 const link=page.locator('.asset-page-contents a[href="#asset-constituent-coverage"]');await link.focus();await page.keyboard.press('Enter');await expect(page).toHaveURL(/#asset-constituent-coverage$/);await expect(page.locator('#asset-constituent-coverage')).toBeVisible();
 for(const id of['asset-evidence-checks','asset-conclusion-register']){await page.locator(`.asset-page-contents a[href="#${id}"]`).click();await expect(page).toHaveURL(new RegExp('#'+id+'$'));await expect(page.locator('#'+id)).toBeVisible();}
 await page.goto(`data-sources/?lang=${locale}#research-asset-implementation`);await expect(page.locator('#research-asset-implementation')).toContainText('2026-11-01');await expect(page.locator('#research-asset-implementation a[data-version-manifest]')).toHaveCount(1);
});
test('version context and non-chart destinations remain readable without scripts',async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();await page.goto('research/asset-implementation/');await expect(page.locator('#asset-evidence-version')).toContainText('2026-11-01');await expect(page.locator('main details:not([open])')).toHaveCount(0);await page.locator('.asset-page-contents a[href="#asset-conclusion-register"]').click();await expect(page.locator('#asset-conclusion-register')).toBeVisible();await context.close();
});
