# Risk-rule validation and execution diagnostics

[简体中文](execution-validation-suite.zh-CN.md)

This study freezes the CNY1 rule before additional execution runs and tests what changed, whether another year reproduces the effect, and how simulated exits respond to different execution constraints. It extends the preserved research workflow, with no changes to the original 18 public scenarios.

The [frozen protocol](execution-validation-protocol.json) records the rule, windows, full execution configurations and evaluation metrics. The 2024 rules were developed after observing failures. Existing 2025 evidence and the feasibility screen have already been inspected, so 2025 is retrospective cross-year validation, not unseen out-of-sample evidence. No parameter is selected using subsequent 2025 results.

The 2024 arms are baseline, price-only, additional ST-availability checks, confirmed termination decisions only, and combined guards. They share four source-bound noncash impairment declarations. The 2025 arms separate price and ST checks; termination-announcement coverage is incomplete and that guard is explicitly untested. An empty event table cannot establish complete announcement coverage.

Preparation retains the full selection universe and verifies original selected rows and targets exactly. The 2025 daily manifest differs from the previous preparation. A dedicated, explicit lineage treatment permits that manifest change only after exact selected-row and baseline-target checks; it does not waive other source checks or prove historical identity of the original unarchived full candidate universe.

Per-symbol accounting separates net trade cash, paid and unpaid dividends, stock rights, ending inventory and fees. Paired accounting differences identify which securities contributed to the return difference; they are not causal estimates of what would happen while holding all other positions fixed. Exit diagnostics report attempts, fills and retained shares separately. Observable suspension, limit and participation constraints overlap and do not establish a unique reason for every expired order.

Stress profiles vary capital, participation rate, release horizon and slices. These measure sensitivity of bounded minute-bar execution. They do not model queue priority, auction access, replenishment or the strategy's own market impact, and cannot establish live capacity.

Automated preflight checks input hashes, complete-universe retention, session coverage, target timing, prices, corporate actions and source bindings. Actual simulation still must pass held-inventory NAV and ownership gates. Independent ledger diagnostics then reconcile account outcomes. Passing these checks does not establish revision-safe PIT.

Exact execution inputs, configurations, valuation declarations and provider hashes may permit verified ledger reuse between identical arms. Such receipts say `verified_ledger_reuse`, cite the original immutable ledger and preserve all source hashes; they are never presented as additional independent simulations.

## Findings

The price guard's improvement did not reproduce in the second year. In 2024 it mainly avoided two securities that later became difficult to exit. ST-availability and termination-announcement guards alone did not change actual fills in this sample. All tested 2025 price/ST arms have identical targets and execution outcomes, with no incremental return.

These are full-year minute-model account returns after modeled fees. All 2024 arms share four noncash full-impairment declarations: shares remain held and no sale proceeds are created. The termination guard remains untested in 2025.

| Year and arm | CNY1m | CNY10m |
| --- | ---: | ---: |
| 2024 baseline, ST-only, termination-only | 4.7317% | 3.6037% |
| 2024 price-only, combined | 12.3079% | 11.1010% |
| 2025 baseline, price-only, ST-only, price/ST | 70.2800% | 72.6307% |

For CNY1m, the 2024 improvement is approximately CNY75,762: CNY47,360 in gross P&L changes for the two avoided securities, CNY28,874 from other replacements and rebalancing, less CNY472 in additional fees. For CNY10m the corresponding amounts are CNY749,736, CNY476,509, CNY277,884 and CNY4,657. Existing 002621 inventory remains. This conserved accounting attribution is descriptive, not a causal estimate or evidence of general predictive validity.

## Execution sensitivity

All rows use the 2024 combined arm and identical impairment declarations. Unless specified, capital is CNY10m, participation 5%, release horizon 330 minutes, one release slice and one-minute latency. Completion is target-notional weighted, not an order-count fill rate or a live-capacity estimate.

| Profile | Account return | Target-notional completion |
| --- | ---: | ---: |
| Control | 11.1010% | 89.7397% |
| 1% participation | 14.5060% | 80.5644% |
| 3% participation | 12.4459% | 89.2028% |
| 10% participation | 10.9268% | 90.1199% |
| 30-minute horizon | 11.7348% | 85.6801% |
| 120 minutes, five slices | 12.0231% | 86.5211% |
| CNY100m | 14.7280% | 74.7599% |

Return and completion do not move together. Reduced fills change cash, inventory and timing, which can improve this particular sample's strategy return. Higher CNY100m return does not establish greater capacity. These outcomes must not be used to select an execution profile and then claim independent validation. The model does not estimate orders' feedback on market prices.

Exit diagnostics retain 65 failed sell attempts for 002621 and ending inventories of 13,900 shares at CNY1m and 138,500 at CNY10m. A zero impairment mark is not a completed exit. Price limits, available volume and release timing describe overlapping observable constraints; dates with no order do not establish continuous exit attempts.

Descriptive regimes use information available from the previous session: prior five-session mean turnover below 80% of the prior twenty-session mean, or at least 2% of observed main-board securities closing at their lower limit in the prior session. Low-liquidity/prior-down-limit counts are 5/26 in 2024, with one overlapping session, and 0/4 in 2025. Each year's first twenty sessions lack within-window history. Labels may fall on a rebound following a crash and do not describe contemporaneous crash-day returns.

## Reproduction and remaining evidence

The 24 scenario records comprise twelve actual simulations and twelve hash-verified ledger reuses. Identical arms share economic outcomes; these are not 24 independent experiments. The original eighteen public results are preserved.

Use external paths defined by the project's data contract and the locked research environment with the formal minute-execution provider. Outputs must be new isolated directories, without overwriting sources or shared results:

```bash
PYTHONPATH=src python scripts/prepare_execution_validation_suite.py \
  --data-root "$PLATFORM_DATA" --base-prepared "$BASE_PREPARED" \
  --output "$PREPARATION_ROOT" --protocol docs/execution-validation-protocol.json \
  --source-packet "$SOURCE_PACKET" --mode combined \
  --profile fees_1m --profile fees_10m
PREPARED="$PREPARATION_ROOT/combined"
python - "$PREPARED" <<'PYPROFILES'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
inputs = json.loads((root / 'inputs.json').read_text())
(root / 'requested-profiles.json').write_text(json.dumps(
    inputs['experiment_study']['authorized_profiles'], indent=2) + '\n')
PYPROFILES
PYTHONPATH=src python scripts/run_execution_validation_suite.py \
  --output "$PREPARED" --profiles "$PREPARED/requested-profiles.json"
PYTHONPATH=src python scripts/prepare_execution_stress_profiles.py \
  --prepared "$PREPARED" --output "$STRESS_PREPARED" --profile fees_100m
PYTHONPATH=src python scripts/run_execution_validation_suite.py \
  --output "$STRESS_PREPARED" --profiles "$STRESS_PREPARED/requested-profiles.json"
PYTHONPATH=src python scripts/prepare_execution_market_regimes.py \
  --prepared "$PREPARED" --output "$REGIME_PREPARED"
```

For 2025 use `baseline`, `price_only`, `st_only` or `price_st`, without the 2024 announcement packet. The explicitly documented daily-manifest revision requires `--allow-daily-manifest-revision` and exact original selected-row and target checks. Diagnostic entry points are `diagnostics.analyze_run`, `analysis_summary.compare_reports` and `analysis_summary.market_regime_summary`; these are research tools rather than live-order interfaces.

Next priorities are complete 2025 announcement evidence and a pre-fixed test on a genuinely unseen period. Revision-safe historical data, executable post-delisting quotes, queue behavior and own market impact remain unresolved. This study's checks do not replace that evidence.
