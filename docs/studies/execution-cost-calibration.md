# Real-order execution calibration entry

[中文](execution-cost-calibration.zh-CN.md)

The canonical input validator, benchmark measurement and chronological holdout entry are implemented. A deterministic 80-parent,20-date synthetic integration run verifies the pipeline. No broker execution files have been supplied for this study: actual-order calibration and causal own-impact identification remain incomplete.

This is a research diagnostic, not a new execution simulator. Vendor adapters belong to quant-market-data-platform; general execution models belong to quant-platform. The topic measures supplied executed orders without inventing missing fills or charges.

## Input contract

Keep a private input directory with `manifest.json` and exactly one CSV or Parquet for each of `orders`, `fills`, `quotes`. Prices are CNY; quantities are shares. Every timestamp carries an explicit UTC offset; do not silently interpret broker-local clocks. The manifest must declare schema `ashare_execution_costs.canonical_orders.v1`, `data_kind` (`actual`, `paper`, `synthetic`), `source`, `price_unit: CNY`, `quantity_unit: share`, `time_contract: explicit_UTC_offset`, `fees_contract: actual_parent_total_CNY_once`.

| File | Required columns | Meaning |
| --- | --- | --- |
| orders | parent_order_id,symbol,side,target_qty,decision_time,arrival_time,end_time,state,fees_cny | One complete parent lifecycle; side buy/sell; terminal state filled/cancelled/expired/rejected. Fees are the actual parent total, including all components, counted once. |
| fills | fill_id,parent_order_id,fill_time,qty,price | Unique actual fills, including partial fills; orphan/duplicate/overfilled/late fills fail validation. An empty fill file retains its headers. |
| quotes | symbol,quote_time,bid,ask | Unique two-sided quote snapshots. Optional available_time records when received; market_level is a contemporaneous positive broad-market benchmark for response analysis. |

Optional order columns `predicted_arrival_bp` and `prediction_time` supply a model prediction created no later than arrival. Timestamp validation does not authenticate how that prediction was generated; prediction provenance requires separate review. If quote reception times are absent, availability equals exchange quote time by explicit assumption. Clock synchronization and transport latency then remain unverified.

Do not treat exported child orders as independent parents. Preserve the broker/system's parent link, amendments and terminal lifecycle; when unavailable, keep the source uncalibrated until a reviewed adapter can resolve it. Exclude account identifiers and credentials from the canonical schema, while retaining the private source receipt.

## Accounting and validation

For sign s=+1 buy,-1 sell, full shortfall in CNY is:

` s * sum(fill_qty * (fill_price - decision_mid)) + s * unfilled_qty * (terminal_mid - decision_mid) + actual_parent_fees `

Divide by `target_qty * decision_mid` and multiply by10000 for bp. The signed arrival execution cost compares fill VWAP to arrival midpoint on filled shares. Decision-to-arrival delay is separate. Zero fills have no executed-price metric but retain unfilled opportunity cost. Negative costs are possible. These measurements include market and signal movement; none identifies causal own impact.

Only quotes dated and available at or before the relevant event are used, with default maximum age1000ms. Missing/stale benchmarks leave the parent visible and ineligible for full calibration. No next quote, interpolation, old daily close or missing fee estimate is substituted. Market-adjusted responses at30,300,1800 seconds start at terminal midpoint, subtract broad-market log return, and retain missing horizons. Terminal time can be cancellation/expiry, so this is a terminal-order response rather than necessarily last-fill response.

Training uses earlier whole UTC arrival dates; later dates form the test set. Training parents whose terminal outcomes are not available before the first test arrival are purged. A training-only side median is the transparent baseline, with holdout MAE,bias and90th-percentile absolute error. At least20 training and10 test parents are required; unseen test sides block evaluation. Actual,paper and synthetic orders cannot train together. Supplied predictions are scored separately; source provenance and strategy timing still need review. Side aggregates require at least20 parents and20 valid observations per displayed metric. These are sample diagnostics, not population confidence intervals.

## Run and review

```bash
PYTHONPATH=src uv run --locked python scripts/run_execution_cost_calibration.py \
  --input-root "$PRIVATE_ORDER_INPUT" --output-root "$NEW_EXTERNAL_RUN" \
  --max-quote-age-ms 1000 --min-group-orders 20
```

A new output directory is required. Private parent measurements, detailed validation and a hash receipt stay outside Git. `aggregate.json` contains fixed side groups and allowlisted metrics, no parent IDs,symbols,event times or private paths. Review it and the source kind before any publication. The `actual_order_calibrated` flag requires actual-declared data and a completed chronological baseline evaluation; it refers to that observational cost baseline only. Source authenticity, causal impact, queue modeling and capacity are separate gates.

Next calibration should compare order-size/ADV, participation, volatility, spread, duration and execution-method models against this baseline, with training-only preprocessing and parent/date isolation. Start with actual logs already generated by ordinary trading; this work does not authorize placing new trades. Any later controlled execution comparison must separately specify allocation, market-state controls and a valid identification design.
