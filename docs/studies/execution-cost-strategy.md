# Existing microcap strategy cost sensitivity

This companion compares gross, assumed fees, and fees plus borrowed static book
costs on the existing January–March 2025 microcap diagnostic. It is diagnostic
execution sensitivity, not verified net alpha or live strategy capacity.

Two comparisons answer different questions:

- **Frozen path accounting:** retain the original holdings P&L and executed or
  missed fills. Reconcile the original simulator's flat 5 bp cost with the fill
  and daily performance ledgers before adding back its cash debit. Subtract
  replacement fees and static debits cumulatively in CNY. This is an algebraic
  counterfactual, not a fee-free strategy rerun. Negative cash is reported as a
  funding shortfall; an unfunded counterfactual is not executable net performance.
- **Shared simulator reruns:** load the original content-addressed pricing and
  targets, then reuse `quant-platform`'s `simulate_execution_adjusted_nav` at
  CNY 10 million, 100 million and 1 billion. Run gross, assumed fee-only, and
  fee plus borrowed 10k and 1m static cost anchors. Orders are reexecuted under
  the original 5% of daily amount participation proxy, T+1, price-limit flags,
  five-day buy and ten-day sell windows. Cash and missed fills can change.

The original 5 bp is disabled in reruns and replaced in overlays; it is never
added to the new static anchor. Fees assume inclusive commission 1 bp on each
side, no minimum, and seller stamp duty 5 bp. The source period follows the
[2023-08-28 stamp duty reduction](https://shanghai.chinatax.gov.cn/zcfw/zcfgk/yhs/202308/t468451.html).
The commission is a sensitivity assumption, not a broker tariff. Inclusive
commission avoids separately adding a transfer fee; venue differences and
minimum commissions remain unmodeled.

All four pilot notional anchors (10k, 100k, 1m, 10m) are separate frozen-path
scenarios at every capital, rather than capital-calibrated estimates. Their
buy and sell P50 values condition on full ten-level book coverage. Each summary
retains the pilot coverage rate and the notional-weighted share of scaled
requested orders exceeding the anchor. That share compares order sizes only;
it does not estimate matched-book coverage. No missing depth is interpolated.

The 60% one-way stress trades 60% of current NAV on **each** side per session.
Its daily debit fraction is `0.6 * (buy_bp + sell_bp) / 10000`; cost-only NAV
compounds this debit for 250 sessions. The linear debit sum is reported separately.
It is a turnover stress, not the strategy's observed turnover or predicted return.

## Reproduce

The optional shared simulator must be available in the environment. Use a new
output directory under the owning project's configured data root:

```bash
PYTHONPATH=src python scripts/run_execution_cost_strategy.py \
  --source "$QUANT_DATA_ROOT/quant-market-research/outputs/microcap_execution_diagnostic_2025q1_published_20260928" \
  --pilot "$QUANT_DATA_ROOT/quant-market-research/ashare_execution_costs/pilot-20261012-v2/summary.json" \
  --output "$QUANT_DATA_ROOT/quant-market-research/ashare_execution_costs/strategy-new-run"
```

The fixed source has 56 valuation sessions, 23,030 fill records and 23,110 order
records, with original initial capital CNY 1 million. Output includes aggregate
CSV daily ledgers, scenario summaries, turnover stress and a receipt with source
hashes. It exports no security symbols, order IDs or local source paths.

Original release times, corporate actions and delisting settlement remain
unverified. Adjusted daily closes and daily liquidity cannot represent intraday
queues, book resilience, permanent impact or true capacity. Original orders do
not encode why an amount remained unfilled, so limit and suspension attribution
is not fabricated. The later 2026 pilot is borrowed across dates and securities;
its covered-order medians cannot establish realized execution or net alpha.
