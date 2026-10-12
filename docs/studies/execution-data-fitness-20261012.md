# Existing execution-data fitness

Raw identity/date/clock scans on January 4, 2021 and April 16, 2026 reproduce every saved earliest-minute selection with zero mismatches. This covers two declared dates and the modulo-37 stock sample, not the complete warehouse or historical eligibility.

The first date has 26,070 of 26,070 expected observed-security minutes. The second has 32,694 of 33,654, missing 960 bins across 80 stocks at twelve minutes, 09:32–09:36 and 09:54–10:00. Same-day positive-trading-amount daily records contain 110 and 142 sampled stocks respectively; none lacks continuous-session raw quotes entirely. This retrospective cross-check cannot establish the historical eligible universe or explain the gaps. Raw depth columns were not fully rescanned; large-file hashes were not recomputed, with before/after file size and mtime receipts retained.

Saved positive-price/quantity trades are checked against OrderID and, where available, DBOrderID separately, using security/channel scope only where both streams supply channels. Categories distinguish unique and repeated keys whose earliest file timestamp is no later than trade, keys appearing only later, and missing keys. Equal timestamps are counted separately and do not establish exchange order. Historical Shanghai order records remain absent; newer Shenzhen retains nonpositive-price special records outside ordinary-trade matching.

Common-stock opening paths now span 1,000, 10,000 and 100,000 shares, both sides and three modes in a fixed 09:30–09:35 window. One historical path with an invalid book is excluded explicitly. There are 3,798 scenarios, with 105/106 included stocks on the early/recent date; fresh terminal benchmarks exist for 105/43. Missing data prevents an unqualified temporal algorithm comparison. An independent scalar depth walk reconciles all scenarios, 20,867 level fills and 36 aggregate cells. These are conditional counterfactuals without fees, queues, lot rounding, own impact or participation caps.

A 0.4% all-in assumption is 40 bp per side if charged on each trade, or 20 bp per side under an equal split of a 40 bp round trip. At 250 days with buys/sells each 60% of constant NAV daily, linear expenditures are 120% and 60%; neither is a realized NAV loss. These are stress assumptions and must not be charged again as fees plus the same slippage. [Chinese factor-model research](https://doi.org/10.1016/j.irfa.2023.102975) uses a historical 37 bp estimate derived from 2009–2016 spread research; that is not a contemporary universal calibration.

Run in an environment containing duckdb, pandas, pyarrow and quant-platform, with new external output:

```bash
PYTHONPATH=src python scripts/run_execution_data_fitness.py \
  --spec "$EXECUTION_EXPANSION_SPEC" \
  --saved "$EXECUTION_EXPANSION_SAVED" \
  --output "$NEW_EXTERNAL_RUN"
python -m pytest tests/studies/test_execution_cost_fitness.py -q
```

Priority follow-up is another local copy or acquisition logs for the synchronized minute gaps; verified vendor event/cancel dictionaries and exchange ordering; and actual orders/fills/fees for slippage calibration. Public aggregates exclude security IDs, raw events and private paths.
