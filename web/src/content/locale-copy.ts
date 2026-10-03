import type { PublicPage } from "./public-registry";

const englishCopies: Record<string, { title: string; summary: string }> = {
  overview: { title: "Research overview", summary: "What each study found, which dates it covers, and what remains uncertain." },
  research: { title: "Research topics", summary: "Start with a research question, then see the main finding and its limits." },
  cashflow: { title: "Cash Flow and Dividends", summary: "What historical cash-flow groups returned, how long losses lasted, and which checks remain open." },
  "cashflow-recovery": { title: "Cash-Flow Recovery", summary: "How long past declines lasted, how well the results were rebuilt, and what real trading would still require." },
  microcap: { title: "Micro-cap Research", summary: "What historical small-stock portfolios returned and lost, with their data gaps shown." },
  "cross-market-liquidity": { title: "Cross-market Liquidity", summary: "How much stocks traded in each market and whether those figures can be compared." },
  indices: { title: "Indices and Long-run Returns", summary: "Which index and ETF histories are included, and why their returns use different definitions." },
  style: { title: "18 Years of Style Factors", summary: "How value, size, and other stock groups behaved across years and market conditions." },
  "pb-roe": { title: "Historical PB and ROE Comparison", summary: "Whether adding profitability data changed a historical valuation comparison using the same stocks." },
  liquidity: { title: "Liquidity Research", summary: "How active trading was in the sampled stocks, how much data is available, and what cannot yet be inferred." },
  "low-turnover": { title: "Low-turnover Factor", summary: "What lower trading activity tracked in past data, how the gap changed after controls, and whether a real portfolio could trade." },
  "research-closeout-status": { title: "Research Closeout Status", summary: "Project status, evidence boundaries, and open verification items." },
  "low-turnover-method": { title: "Low-turnover Method", summary: "Methods, execution assumptions, and validation evidence." },
  "pb-roe-method": { title: "Historical PB and ROE Comparison", summary: "Paired valuation and profitability results, candidate-universe audit, and validation limits." },
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
