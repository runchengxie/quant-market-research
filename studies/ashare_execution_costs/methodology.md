# Measurement protocol

## Baseline and ledger

Define buy and sell turnover separately as executed notional / pre-trade NAV. For balanced full-investment rebalances without flows, one-way target turnover is half the sum of absolute differences between target weights and drifted pre-trade weights. Target and executed turnover differ when orders fail.

Simple annual cost = sum over sessions of (fees + execution shortfall) / session NAV. A constant-NAV example uses 250 × [buy turnover × (buy fees + buy slippage) + sell turnover × (sell fees + sell slippage)]. Compound net NAV requires the actual return and cost path. Track commissions, taxes, transfer fees and included levies with effective dates and invoice evidence. Audit quant-platform's dated and detailed fee models before combining them with separate slippage models.

## Static book cost

For positive valid bid/ask quotes, mid = (best bid + best ask) / 2. BuyCost(Q,t) = 10000 × (ask VWAP(Q,t) / mid − 1). SellCost(Q,t) = 10000 × (1 − bid VWAP(Q,t) / mid). Q is shares in validated units; notional budgets must be converted using consumed level prices, board-lot rules and available cash. Include covered quantity and fraction for every requested size. If ten levels cannot cover Q, label the estimate incomplete and report cost for covered quantity separately; never present it as full-order cost.

These metrics include half-spread and static depth cost. They assume immediate access to displayed liquidity. They exclude latency, queue priority, replenishment and causal impact of the researcher's order. Do not add a separate spread charge to them. Invalid/crossed books and auctions require separate handling, not silent inclusion in continuous trading.

## Validation and strategy use

Stratify by market cap, lagged ADV, volatility, time of day and market state. Definitions and lag windows must be fixed before estimation. Keep stock/day coverage, missingness and exclusion rates alongside P50/P90/P95. Use date/stock clusters for uncertainty rather than treating snapshots as independent observations. Split calibration and evaluation by time; report both stock overlap and period overlap.

Real-order implementation shortfall needs side, decision timestamp/price, quantity, fills, cancellations, fees and end-of-horizon value of unfilled quantity. Distinguish realized execution cost from opportunity cost. Avoid summing a static book estimate and dynamic impact estimate that cover the same price move.

For planned CNY 10m/100m/1bn portfolios, derive each stock order from target weights and map it to lagged ADV and execution-window volume. Portfolio turnover alone cannot determine participation or capacity. Compare gross, fee-only and calibrated modeled returns; include T+1, suspensions, price limits, partial fills and cash retention. Test buy/hold buffers and slower trading jointly with signal decay. Publish modeled capacity separately from actual-order validation.
