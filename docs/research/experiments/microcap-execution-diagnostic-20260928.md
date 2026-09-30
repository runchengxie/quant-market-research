# Microcap portfolio execution diagnostic

[Chinese version](microcap-execution-diagnostic-20260928.zh-CN.md)

The `microcap-execution-diagnostic` experiment selects the smallest N eligible stocks from cleaned daily data using post-close market capitalization, ST status, suspension, and listing-state rules. Each decision date has an independent research clock. The input is submitted by content hash to `quant-backtest-runtime`, whose worker calls the public execution simulator in `quant-platform`.

The diagnostic uses a 5% participation rate, T+1, daily limit-up and limit-down blocking, unfilled cash, and a simplified 5-basis-point per-trade cost. Prices use the cleaned daily `adj_close` proxy. Targets, orders, fills, daily cash, and NAV ledgers remain outside the repository. Only runtime-validated ledgers are copied into the diagnostic directory, and `summary.json` records the job ID.

This diagnostic ledger is separate from historical paper returns. It is an execution feasibility check, not a live-trading result or strategy promotion.
