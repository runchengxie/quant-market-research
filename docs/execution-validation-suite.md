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
