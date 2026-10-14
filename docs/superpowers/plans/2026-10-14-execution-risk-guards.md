# Causal risk guards and executable exits

**Goal:** Compare the preserved small-cap baseline with an explicit risk-guard variant, including trapped holdings and executable exits.

**Authorization:** User approved the proposed sequence: preserve baseline, add dated risk guards, enforce real execution constraints, and independently cross-check successor-board quotes.

**Architecture:** Research-side target generation adds a prior-close minimum price hypothesis, availability-aware ST validation and hash-bound confirmed termination decisions. The existing minute provider already handles sell attempts, T+1, limits, participation and cash conservation. Do not fabricate a successful exit or remove inventory. Use the same full-impairment and optional single-source-quote valuation assumptions for matched comparisons.

**Scope:** Daily rebalancing, CNY 1m and CNY 10m first. A CNY1 prior-close threshold is an explicit experimental parameter, not a universal statutory face value. Signals use prior-session information; announcement guards are known by decision time. No ex-post three-name exclusion or later-date membership filtering.

- [x] Inspect baseline: ST/name/suspension eligibility exists. Two names entered below CNY1; the third entered before ST information and later lacked an executable sale.
- [x] Add tested research risk-target API without changing default targets; availability, future invariance, threshold boundary, buffering and reason audit.
- [x] Bind full-universe inputs and inspect any additional selected securities; complete source/action/suspension coverage before running. Save and hash the full panel, require exact original selected rows, disclose missing historical full-universe archive.
- [x] Run matched risk-guard capital pilots and compare with source-identical preserved baselines, including failed exits, retained shares, fees and NAV. Both arms use four declarations; the added unheld Jielong event creates zero-quantity blocked order records only.
- [x] Independently reconstruct accounts and causal signal/exit timing; distinguish emitted orders from fills. Four complete account reconstructions pass; retain the first strict-artifact diagnostic and explain generated IDs/annotations and target ordering separately.
- [x] Bounded successor-board price cross-check; preserve unresolved observations and field-unit limitations. No independently established historical closing trades; chart corroboration and lot/tick rules remain insufficient.
- [ ] Bilingual explanation, relevant checks, reviewed PR/merge/publication and cleanup of this task only.
