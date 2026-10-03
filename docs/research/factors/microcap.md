# Microcaps: return evidence and underwater periods

[Chinese version](microcap.zh-CN.md)

This page describes reconstructed historical rules and risk characteristics. It is not a Wind index replication and does not represent a directly tradable strategy.

## Plain-language takeaway

The clearest result here is about risk: portfolios rebuilt from small stocks had deep losses and sometimes took years to recover their previous highs. Some early returns are still being checked, and delisted stocks, historical membership, and actual trading have not been fully reconstructed. Treat the return series as a research record, not as an index or an account result.

An **underwater period** is the time a portfolio stays below its previous high until it passes that high again. **Maximum drawdown** is the largest fall from a high to a later low. **NAV** (net asset value) is the portfolio-value series scaled to a starting level. For each measure, missing-price rules also matter.

The current source coverage extends through 2026-09-17. The next-day return audit for the minimum-market-cap proxy is computable through 2026-09-16. Portfolio sizes are N = 50, 100, 200, 400, and 800.

The [microcap execution diagnostic](../experiments/microcap-execution-diagnostic-20260928.md) uses a separate public execution-simulation ledger and must not be joined directly to historical paper returns. Differences in data cleaning, decision clocks, fills, and cost assumptions remain part of the evidence boundary.
