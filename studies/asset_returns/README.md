# Long-horizon asset returns

[中文](README.zh-CN.md)

This study connects existing cash-flow, valuation, small-cap, liquidity and execution-cost topics. It separates historical observations, accounting decompositions and hypothetical cash-flow scenarios. It does not estimate forward expected returns or implement a trading engine.

## Reproduce a frozen monthly study

```bash
uv run --locked --extra dev python -m market_research.studies.asset_returns.run \
  --input "$TASK_INPUT/monthly.csv" \
  --metadata "$TASK_INPUT/metadata.json" \
  --output "$TASK_RESULTS/run-01"
```

Resolve `TASK_INPUT` and `TASK_RESULTS` from the owning project's configured data root. Output must be a new directory outside source repositories. The runner records input and metadata SHA-256 hashes; it never switches a shared publication alias.

`monthly.csv` requires `date,price,total`. Dates are consecutive calendar month ends, with levels taken from verified final trading sessions. `month_end_levels` requires an independently verified calendar and an exact quote on each final session; it cannot establish that the supplied calendar itself is complete. It checks monthly endpoints, not every intervening day.

Optional columns: `cpi` (chained price level, never year-on-year rates), `gold`, `bond` (wealth index), `benchmark` (total return), `pe`, `eps`, `cash_per_unit`. Financial series must already use one currency. Use `convert_currency` with target-currency units per local unit; it preserves the asset/FX interaction. No forward filling or missing-return zero filling is performed.

Metadata schema:

```json
{
  "schema_version": 1,
  "source_revision": "exact research code revision",
  "series": {
    "price": {"currency": "CNY", "return_basis": "price", "source_id": "frozen asset identifier", "coverage_verified": true},
    "total": {"currency": "CNY", "return_basis": "total_return", "source_id": "frozen asset identifier", "coverage_verified": true}
  }
}
```

Every additional column needs equivalent metadata; CPI/PE use dimensionless currency identifiers. `coverage_verified` is an explicit operator assertion supported by retained evidence, not something the runner can certify from two columns. Source identity must link to frozen inputs and their receipts. Raw responses remain with the data owner.

## Interpret the outputs

- **Sources:** geometric `total / price` decomposition. The residual includes reinvestment mechanics and is not a cash dividend yield. Component CAGRs compound, rather than add.
- **Holding periods:** 12/36/60/120-month overlapping windows, nominal and optional real losses, annualized endpoint returns, and recovery entries. Unfinished entries remain censored; the final entry has no follow-up. Monthly recovery can miss earlier intramonth touches and is not a forecast of waiting time. Existing recovery fields called `trading_sessions` mean observation intervals in this monthly study.
- **Earnings:** `price = EPS × PE` reconciliation. EPS inferred from price/PE is explicitly marked. Supplying EPS does not certify independent financial scope or constituent continuity. Fixed-constituent analysis, issuance, delistings and corporate-action attribution remain separate prerequisites.
- **Diversification:** monthly and 36-month rolling correlations, plus asset returns during negative equity months. Constant or insufficient samples produce unavailable correlations. Equal-weight monthly mixes assume simultaneous frictionless rebalancing; 0/50/100-bp annual wealth drags are sensitivities, not calibrated trading costs. Do not treat these as implemented portfolio accounts.
- **Relative premia:** geometric relative wealth and its drawdown/recovery. A realized difference does not establish a causal risk premium. Small-cap is not microcap; calibrated microcap costs and capacity remain owned by the existing execution study.
- **Cash scenarios:** `cash_per_unit` must use split-adjusted units consistent with prices. The model assumes entitlement and payment in the same month, paid on beginning units before month-end withdrawals. Set `cash_timing` to `same_month_entitlement_and_payment` to opt into this approximation. Do not feed raw ex-date/pay-date distributions directly. Cash is retained without interest or reinvestment; withdrawals use cash first, then sell units. Unsatisfied withdrawals and costs remain explicit. Requested withdrawals are nominal, and initial purchase costs and taxes are excluded.

## Publication and next evidence

Only reviewed derived aggregates may enter the website. Complete runs, row-level provider inputs and credentials remain outside Git. Supplier access, complete history, semantic validation and publication rights are distinct checks. The SBBI China 2025 report is an external comparison, not a replacement input or a forecast.

Before publishing independent earnings explanations, recover constituent/share ledgers and original financial vintages. Before publishing actual withdrawal accounts, implement or reuse an entitlement-aware platform ledger. Before extending six-market conclusions, complete ETF distributions, FX timestamp alignment and execution calibration. Preserve existing topic ownership and factor-observatory publication contracts.

## Follow-up evidence

The [second-round findings](followup-20261031.md) add endpoint stability, relative waiting, three ETF return layers, fixed allocation rules and annual constituent-cohort audits. The [follow-up protocol](followup-protocol.md) records exact reproduction commands, costs and unresolved earnings prerequisites. This supplements the first-round snapshot without changing it.

- Evidence closure / 证据核查：[English](closure-20261031.md) · [中文](closure-20261031.zh-CN.md)
