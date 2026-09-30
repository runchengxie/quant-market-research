import type { PublicPage } from "./public-registry";

const englishCopies: Record<string, { title: string; summary: string }> = {
  cashflow: { title: "Cash Flow and Dividends", summary: "Long-run factor performance, recovery tests, and limitations." },
  "cashflow-recovery": { title: "Cash-Flow Recovery", summary: "Recovery, replication, and implementability evidence." },
  microcap: { title: "Micro-cap Research", summary: "Evidence on size, turnover, and sample coverage." },
  "cross-market-liquidity": { title: "Cross-market Liquidity", summary: "Liquidity definitions and replication across markets." },
  indices: { title: "Indices and Long-run Returns", summary: "Index samples, classification filters, and long-run return evidence." },
  style: { title: "18 Years of Style Factors", summary: "Annual factor performance, Barra definitions, and research boundaries." },
  "pb-roe": { title: "Historical PB and ROE Comparison", summary: "Five ranking methods on one candidate universe, including missing ROE and quality checks." },
  liquidity: { title: "Liquidity Research", summary: "Coverage, data definitions, and verifiable findings." },
  "low-turnover": { title: "Low-turnover Factor", summary: "Long-run performance, execution ledger, and replication evidence." },
  "research-closeout-status": { title: "Research Closeout Status", summary: "Project status, evidence boundaries, and open verification items." },
  "low-turnover-method": { title: "Low-turnover Method", summary: "Methods, execution assumptions, and validation evidence." },
  "pb-roe-method": { title: "Historical PB and ROE Comparison", summary: "Paired valuation and profitability results, candidate-universe audit, and validation limits." },
  "microcap-method": { title: "Micro-cap Method", summary: "Research methods, coverage, and limitations." },
  "microcap-execution-diagnostic": { title: "Micro-cap Execution Simulation Diagnostic", summary: "Execution ledger, missing settlement events, and verifiable boundaries." },
  "smallcap-turnover-history": { title: "Small-cap Turnover History", summary: "Definitions and findings from the historical small-cap turnover study." },
  "barra-factor-dictionary": { title: "Barra Factor Dictionary", summary: "Definitions checked for 19 historical factors and their core proxies." },
  "barra-source-inventory": { title: "Barra Source Inventory", summary: "Sources, versions, and verification status for Barra factors." },
  "data-sources": { title: "Data and Versions", summary: "Public data snapshots, coverage dates, and build versions." },
};

export function englishCopy(page: PublicPage) {
  return englishCopies[page.id] ?? { title: page.title, summary: page.summary };
}
