import type { PublicPage, TopicId } from "./public-registry";

const topicLabels: Record<TopicId, { en: string; zh: string }> = {
  overseas: { en: 'Overseas lead-lag research', zh: '海外领先指标研究' },
  rotation: { en: "Style and theme rotation", zh: "风格与主题轮动" },
  cashflow: { en: "Cash-flow research", zh: "现金流研究" },
  microcap: { en: "Micro-cap research", zh: "微盘研究" },
  style: { en: "Style research", zh: "风格研究" },
  "low-turnover": { en: "Low-turnover research", zh: "低换手研究" },
  indices: { en: "Index research", zh: "指数研究" },
  "execution-costs": { en: "Trading costs and capacity", zh: "交易成本与容量" },
  liquidity: { en: "Liquidity, costs and capacity", zh: "流动性、成本与容量" },
};

export function topicLabel(topic: TopicId) {
  return topicLabels[topic];
}

const englishCopies: Record<string, { title: string; summary: string }> = {
  "valuation-panel": { title: "Low valuation: historical coverage and ranks", summary: "Five denominator definitions across 130 formations, common-sample ranks and availability limits." },
  "microcap-st-paired": { title: "Microcaps with and without ST: paired short-window exploration", summary: "Paired samples, unresolved exits and the effect of coverage selection." },
  "overseas-forward": { title: "Overseas signals: forward archive protocol v1", summary: "A fixed signal, 08:45 deadline, immutable receipts and evaluation after at least 60 eligible days." },
  "valuation-denominators": { title: "Low valuation: definitions and a current illustration", summary: "Five earnings/equity denominators, six selected issuers and historical availability limits." },
  "microcap-st-audit": { title: "Microcap ST Eligibility and Comparability Audit", summary: "Historical ST rules, delisting exits, weighting, timing and costs differ across study versions." },
  'overseas-leadlag': { title: 'Overseas signals and the A-share open', summary: 'FX and market controls, annual folds and T+1 ETF costs: the Asian increment is unstable.' },
  'overseas-leadlag-method': { title: 'Overseas signals and the A-share open: timing, controls and ETF costs', summary: 'Assumed historical availability, annual folds, FX controls and ETF proxy limits.' },
  rotation: { title: "Style and Theme Rotation", summary: "From style and hotspot signals to ETF portfolios: historical model diagnostics, weekly allocation experiments, and the missing validation steps." },
  "execution-costs": { title: "A-share Trading Costs and Capacity", summary: "Ten selected L2 dates: CNY 100k median static costs are 9.27/8.87 bp; CNY 1m coverage is 62.12%/67.68%. Order-flow audit and strategy sensitivity are published; actual execution remains uncalibrated." },
  overview: { title: "Research overview", summary: "What each study found, which dates it covers, and what remains uncertain." },
  research: { title: "Research topics", summary: "Start with a research question, then see the main finding and its limits." },
  cashflow: { title: "Cash Flow and Dividends", summary: "What historical cash-flow groups returned, how long losses lasted, and which checks remain open." },
  "cashflow-recovery": { title: "Cash-Flow Recovery", summary: "How long past declines lasted, how well the results were rebuilt, and what real trading would still require." },
  microcap: { title: "Micro-cap Research", summary: "What historical small-stock portfolios returned and lost, with their data gaps shown." },
  "cross-market-liquidity": { title: "Cross-market Liquidity", summary: "How much stocks traded in each market and whether those figures can be compared." },
  indices: { title: "Indices and Long-run Returns", summary: "Which index and ETF histories are included, and why their returns use different definitions." },
  style: { title: "18 Years of Style Factors", summary: "How value, size, and other stock groups behaved across years and market conditions." },
  "pb-roe": { title: "Historical PB and ROE Comparison", summary: "Whether adding profitability data changed a historical valuation comparison using the same stocks." },
  liquidity: { title: "Liquidity, Trading Costs and Capacity", summary: "Cross-market profiles, book costs, execution scenarios and quality checks in one study. Actual capacity remains uncalibrated." },
  "low-turnover": { title: "Low-turnover Factor", summary: "What lower trading activity tracked in past data, how the gap changed after controls, and whether a real portfolio could trade." },
  "research-closeout-status": { title: "Research Closeout Status", summary: "Project status, evidence boundaries, and open verification items." },
  "low-turnover-method": { title: "Low-turnover Method", summary: "Methods, execution assumptions, and validation evidence." },
  "pb-roe-method": { title: "Historical PB and ROE Comparison", summary: "Paired valuation and profitability results, candidate-universe audit, and validation limits." },
  "microcap-report": { title: "Small- and Micro-cap Research History", summary: "Reviewed research history, portfolio comparisons, revisions and public methodology appendices." },
  "microcap-method": { title: "Micro-cap Method", summary: "Research methods, coverage, and limitations." },
  "microcap-execution-diagnostic": { title: "Micro-cap Execution Simulation Diagnostic", summary: "Execution ledger, missing settlement events, and verifiable boundaries." },
  "smallcap-turnover-history": { title: "Small-cap Turnover History", summary: "Definitions and findings from the historical small-cap turnover study." },
  "barra-factor-dictionary": { title: "Barra Factor Dictionary", summary: "Definitions checked for 19 historical factors and their core proxies." },
  "barra-source-inventory": { title: "Barra Source Inventory", summary: "Sources, versions, and verification status for Barra factors." },
  "data-sources": { title: "Data and Versions", summary: "Public data snapshots, coverage dates, and build versions." },
  docs: { title: "Methods and dictionary", summary: "Research methods, factor definitions, data sources, and closeout status." },
};

export function englishCopy(page: Pick<PublicPage, "id" | "title" | "summary">) {
  return englishCopies[page.id] ?? { title: page.title, summary: page.summary };
}

export const navigationCopy = { menu: ['Menu', '菜单'], open: ['Open navigation', '展开主导航'] } as const;
