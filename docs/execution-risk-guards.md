# Risk guards and executable exits

[简体中文](execution-risk-guards.zh-CN.md)

In the 2024 development sample, additional risk guards avoided entries into Zhengyuan and Zhongyin and improved account returns under a shared impairment assumption. My Gym remained trapped, so the improvement does not establish avoidance of all delisting risks. Freeze the rules before validating independent years.

This experiment compares the preserved small-cap baseline with additional causal risk guards. Guards change subsequent targets. Minute execution still determines whether an exit fills, and suspended or limit-down positions remain in the account when sales fail.

The baseline already filters ST status, historical names, listing age and suspension eligibility. The experimental variant validates when ST status was available, excludes candidates whose previous-session close was below CNY1, and uses published termination decisions. CNY1 is a research parameter whose opportunity cost must be measured. Decisions are formed at 20:02 in the preceding session and execution starts at 09:32 in the following session.

The original timeline shows that Zhengyuan and Zhongyin first entered below CNY1. My Gym entered above CNY1 before its ST information became effective. Subsequent sale attempts encountered suspension and one-price limit-down bars; these cannot be rewritten as successful exits.

Targets must be rebuilt from the full daily universe. The 109 securities selected retrospectively by the original run must not define the candidate universe. Validated minute bars, corporate actions and factor evidence can be reused only after checking that newly selected securities are within their coverage. Every original prepared input is hash-checked, and the baseline targets must reproduce exactly. Changed inputs or rules require a new output directory.

The complete selection panel is saved externally with its own content hash. Its original 109-symbol rows must match the previous prepared panel exactly. The original baseline did not archive the full candidate panel, so historical identity of all unselected securities cannot be proven retrospectively. A manifest hash does not replace verification of actual price content.

The announcement packet covers four 2024 delistings in the original input set, including Jielong. This is sample coverage, not a market-wide announcement database. Date-only publications become available conservatively at 09:00 on the next exchange session. Future delisting dates and security names do not provide earlier signals.

Matched runs apply the same declared zero valuation after known termination decisions. Legal shares remain; valuation does not generate cash or fills. This prevents a valuation policy change from being mistaken for a risk-filter effect. Previous strict runs, impairment scenarios and single-source successor-board quote scenarios remain preserved.

The initial comparison covers daily rebalancing at CNY1m and CNY10m. The remaining rebalance and slicing matrix is incomplete, and these pilots do not establish live capacity. Review separately examines entry changes, failed exits, trapped shares, opportunity cost in other securities, fees and daily NAV.

The rules were proposed after inspecting the 2024 failures, making 2024 a development sample. Causal information at each rebalance does not turn an improvement into out-of-sample validation. Freeze the rules before testing independent years and market conditions.

Bounded independent quote exploration has not established historical executed closing prices. A separate year-end price chart corroborates an individual value only. Published lot size and tick rules do not establish the vendor API's volume and amount units. The existing single-source quote limitations remain.

## Matched results

The 2024 pilots cover 242 sessions and daily rebalancing of 40 securities, with identical declared full impairment after known termination decisions. These are account returns, not excess returns relative to an index.

| Initial capital | Baseline return | Risk-guard return | Difference |
| --- | ---: | ---: | ---: |
| CNY1m | 4.73% | 12.31% | +7.58 percentage points |
| CNY10m | 3.60% | 11.10% | +7.50 percentage points |

The risk variant never bought Zhengyuan or Zhongyin. My Gym remained trapped at 13,900 and 138,500 shares, with 65 zero-fill sell orders at each capital level. Jielong had previously been bought and sold, with no position when its termination event became effective. Adding that nontrading event produces 120 additional zero-quantity rejected purchase records in each baseline. Financial daily records, holdings and actual execution fields match the earlier impairment baseline; generated order IDs and valuation annotations differ.

Annual transaction costs were CNY8,843.71 and CNY87,073.21 in the risk variant, versus CNY8,372.04 and CNY82,415.83 in the baseline. The improvement is not a fee saving. It combines changed entries, replacement positions and subsequent rebalancing; detailed attribution remains outstanding.

Independent reconstruction of selection order, causal decision and execution times, cash, shares, rights, fees and daily NAV passed for all four runs. Valuation events produce no cash, and affected securities have no actual fills after termination events. The original 18 public scenarios are unchanged and the nine-scenario matrix remains incomplete. These development-sample results do not replace independent-year validation or live capacity estimates.

## Reproduction

Use two new external output directories. Preparation preserves original inputs and rejects selected securities outside the validated execution scope.

```bash
uv run --locked --extra formal --extra duckdb python scripts/prepare_execution_risk_comparison.py \
  --data-root "$QUANT_DATA_ROOT" --base-prepared "$ORIGINAL_PREPARED" \
  --source-packet "$RISK_SOURCE_PACKET" \
  --baseline-output "$BASELINE_OUTPUT" --risk-output "$RISK_OUTPUT"

uv run --locked --extra formal --extra duckdb python scripts/run_execution_cost_minute.py \
  --run-prepared --output "$BASELINE_OUTPUT" --scenario fees_1m --scenario fees_10m
uv run --locked --extra formal --extra duckdb python scripts/run_execution_cost_minute.py \
  --run-prepared --output "$RISK_OUTPUT" --scenario fees_1m --scenario fees_10m
```

Matched receipts bind the common valuation policy and reject separate valuation arguments. Only these two daily-rebalance pilots are allowed. The nine-scenario completion gate remains false; changed policies, inputs or relevant implementations require fresh directories.
