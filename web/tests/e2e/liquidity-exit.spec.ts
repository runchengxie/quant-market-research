import {expect,test} from '@playwright/test';

test('fixed names retain the original denominator, censored tails and independent audit scopes',async({page})=>{
 await page.goto('research/liquidity/?lang=en-US');
 const p=page.locator('#liquidity-exit');await expect(p).toBeVisible();
 await expect(p).toContainText('32,161');await expect(p).toContainText('24,256');await expect(p).toContainText('7,905');
 await expect(p).toContainText('Beyond the selected horizon or unresolved');
 await p.getByRole('combobox',{name:'Subsequent source sessions',exact:true}).selectOption('20');
 const unresolved=p.getByRole('row').filter({hasText:'Budget insufficient with complete evidence'});
 await expect(unresolved).toContainText('56');
 await p.getByRole('combobox',{name:'Budget rule',exact:true}).selectOption('raw');await expect(unresolved).toContainText('55');
 await p.getByText('Continuous-month minutes and revision baseline',{exact:true}).click();
 await expect(p).toContainText('89,250');await expect(p).toContainText('compares identical bytes');
 await expect(p).toContainText('Native bar-interval semantics remain unverified');
 await expect(p.getByRole('link',{name:'Reviewed exit aggregates',exact:true})).toHaveAttribute('href',/exit-exploration\.json$/);
 await p.getByRole('combobox',{name:'Frozen size group',exact:true}).selectOption('0');await expect(p).toContainText('No eligible frozen cohort');
});

for(const [locale,theme] of [['en-US','light'],['zh-CN','dark']] as const)test(`fixed-name exploration fits mobile ${locale} ${theme}`,async({page})=>{
 await page.addInitScript(value=>localStorage.setItem('market-research-theme',value),theme);
 await page.setViewportSize({width:390,height:900});
 await page.goto(`research/liquidity/?lang=${locale}`);
 const p=page.locator('#liquidity-exit');await expect(p).toBeVisible();
 await expect(p).toContainText('32,161');await expect(p.locator('.research-chart canvas')).toBeVisible();
 await p.locator('details summary').click();
 await expect(p).toContainText('89,250');
 await p.screenshot({path:test.info().outputPath(`exit-${locale}-${theme}.png`)});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
 if(theme==='dark')expect(await p.locator('.panel').first().evaluate(e=>getComputedStyle(e).backgroundColor)).not.toBe('rgb(255, 255, 255)');
});
