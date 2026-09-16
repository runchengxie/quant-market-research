import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const [source, overview, routes, pages] = await Promise.all([
  Promise.all([
    "./components/react/ResearchRoutes.tsx",
    "./components/react/research-shared.tsx",
    "./components/react/microcap-page.tsx",
    "./components/react/style-page.tsx",
    "./components/react/cashflow-page.tsx",
    "./components/react/liquidity-page.tsx",
  ].map((file) => readFileSync(new URL(file, import.meta.url), "utf8"))).then((files) => files.join("\n")),
  readFileSync(new URL("./components/ResearchOverview.tsx", import.meta.url), "utf8"),
  readFileSync(new URL("./lib/routes.ts", import.meta.url), "utf8"),
  Promise.all([
    "./pages/research/cashflow/index.astro",
    "./pages/research/microcap/index.astro",
    "./pages/research/indices/index.astro",
    "./pages/research/style-factors-18y/index.astro",
    "./pages/research/liquidity/index.astro",
    "./components/SiteHeader.astro",
  ].map((file) => readFileSync(new URL(file, import.meta.url), "utf8"))),
]);
const site = [source, overview, routes, ...pages].join("\n");
const charts = readFileSync(new URL("./components/MicrocapCharts.tsx", import.meta.url), "utf8");
const researchCharts = readFileSync(new URL("./components/ResearchCharts.tsx", import.meta.url), "utf8");

test("微盘页面保留旧版研究阅读顺序和图表组件", () => {
  assert.match(source, /MicrocapCharts/);
  assert.match(source, /2026 年至今/);
  assert.match(source, /年度收益/);
  assert.match(source, /滚动年化收益/);
  assert.match(source, /最长未回到前高的区间/);
  assert.match(source, /研究解读/);
  assert.match(charts, /dataZoom/);
  assert.match(charts, /AnnualChart/);
  assert.match(charts, /UnderwaterChart/);
});

test("研究路由按主题动态加载页面模块", () => {
  assert.match(source, /import\("\.\/microcap-page"\)/);
  assert.match(source, /import\("\.\/style-page"\)/);
  assert.match(source, /import\("\.\/cashflow-page"\)/);
  assert.match(source, /import\("\.\/liquidity-page"\)/);
});

test("研究总览使用三个研究域和小微盘子主题", () => {
  assert.match(site, /现金流历史研究/);
  assert.match(site, /小微盘历史研究/);
  assert.match(site, /长期风格研究/);
  assert.match(site, /历史研究档案/);
  assert.match(site, /实际账户盈亏/);
  assert.match(site, /跨市场小微盘流动性/);
  assert.match(site, /研究问题与方法/);
  assert.match(site, /19 个因子表现总览/);
  assert.match(site, /逐年合成收益与阶段表现/);
  assert.match(site, /因子相关性/);
  assert.match(site, /历史多空合成收益/);
  assert.match(site, /Barra 风格因子研究（18年）/);
  assert.match(site, /style-factors-18y/);
  assert.match(source, /ResearchBarChart/);
  assert.match(source, /稳定性观察：按月与按阶段/);
  assert.match(source, /区块自助法/);
  assert.match(source, /2015–2019/);
  assert.match(source, /搜索表格内容/);
  assert.match(site, /links = \[/);
  assert.match(source, /时间窗口/);
  assert.match(source, /各市场最近可用数据/);
  assert.doesNotMatch(source, /跨市场研究中/);
});

test("18年风格研究以经验研究问题呈现并明确Barra边界", () => {
  assert.match(site, /18 年 A 股风格因子动态：收益、稳定性与市场阶段/);
  assert.match(site, /这些风格因子在不同 A 股市场阶段是否持续存在/);
  assert.match(site, /Barra-style/);
  assert.match(site, /IC、样本外验证和统计显著性仍待补充/);
});

test("指数研究支持按目录类别筛选长期回报", () => {
  assert.match(source, /指数类别/);
  assert.match(source, /filteredReturns/);
  assert.match(source, /当前公开快照提供十年价格回报/);
});

test("收益图表为缺失值保留 N/A 标记", () => {
  assert.match(researchCharts, /未提供/);
  assert.match(site, /当前窗口没有对应回报口径的数据/);
});

test("小微盘页面呈现成交额研究的覆盖与审计边界", () => {
  assert.match(site, /小微盘成交额研究/);
  assert.match(site, /2008 年起历史口径/);
  assert.match(site, /重叠审计/);
  assert.match(site, /smallcap_turnover\.json/);
  assert.match(site, /microcap_history_2008_2014\.json/);
  assert.match(site, /N=1/);
  assert.match(site, /极端诊断/);
  assert.match(site, /月度汇总/);
});
