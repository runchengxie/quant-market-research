import {expect,test} from '@playwright/test';
const readingSummaries=['factors/low-turnover','valuation-groups','microcap','cashflow','indices','style-factors-18y','overseas-leadlag','style-theme-rotation','liquidity']
  .map(id=>({id,route:`/research/${id}/`}));

for(const width of [1440,900,390])for(const locale of ['en-US','zh-CN']){
  test(`research summaries stay centered and separate at ${width}px in ${locale}`,async({page})=>{
    await page.setViewportSize({width,height:1000});
    for(const report of readingSummaries){
      await page.goto(`${report.route.replace(/^\//,'')}?lang=${locale}`);
      const summary=page.locator('#research-summary');
      await expect(summary).toBeVisible();
      const geometry=await summary.evaluate(element=>{
        const box=element.getBoundingClientRect();
        const main=element.parentElement!.getBoundingClientRect();
        const before=element.previousElementSibling!.getBoundingClientRect();
        const outside=[...element.querySelectorAll('h2,p,dl,dt,dd,details,button,img')]
          .filter(node=>{const rect=node.getBoundingClientRect();return rect.width>0&&(rect.left<box.left-1||rect.right>box.right+1);})
          .map(node=>node.tagName);
        return {center:box.left+box.width/2,mainCenter:main.left+main.width/2,
          left:box.left,right:box.right,top:box.top,beforeBottom:before.bottom,outside};
      });
      expect(Math.abs(geometry.center-geometry.mainCenter),report.id).toBeLessThanOrEqual(1);
      expect(geometry.left,report.id).toBeGreaterThanOrEqual(0);
      expect(geometry.right,report.id).toBeLessThanOrEqual(width);
      expect(geometry.top,report.id).toBeGreaterThanOrEqual(geometry.beforeBottom);
      expect(geometry.outside,report.id).toEqual([]);
    }
  });
}
