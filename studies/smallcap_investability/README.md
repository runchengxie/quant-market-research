# Small-cap research checklist

[Chinese (Simplified)](README.zh-CN.md)

Status tracks deliverables, not investment validity. Done can mean a bounded diagnostic is complete; it does not certify PIT data, executable alpha or a successful hypothesis.

Reviewed: 2026-11-29

The machine-readable source is [task-registry.json](task-registry.json). Waiting means the stated gate is unmet, not that every relevant dataset is absent. No recurring job or prospective registration is created by this checklist.

| ID | Priority | Status | Task | Depends on |
| --- | --- | --- | --- | --- |
| [SC-001](#sc-001) | P0 | Done (bounded deliverable) | Identify retained source versions | — |
| [SC-002](#sc-002) | P0 | Partial | Resolve the 120-session replay discrepancy | SC-001 |
| [SC-003](#sc-003) | P0 | Waiting for evidence | Certify historical membership | SC-001 |
| [SC-004](#sc-004) | P0 | Partial | Reconcile prices and corporate actions | SC-001 |
| [SC-005](#sc-005) | P0 | Waiting for evidence | Fix missing-price and delisting treatment | SC-003, SC-004 |
| [SC-006](#sc-006) | P0 | Done (bounded deliverable) | Specify the common timing contract | SC-001 |
| [SC-007](#sc-007) | P0 | Done (bounded deliverable) | Build matched three-arm target support | SC-001 |
| [SC-008](#sc-008) | P0 | Partial | Extend the shared share/cash ledger | SC-006, SC-007 |
| [SC-009](#sc-009) | P1 | Waiting for evidence | Compare three matched net long-only accounts | SC-003, SC-004, SC-005, SC-008 |
| [SC-010](#sc-010) | P1 | Partial | Version the public descriptor contract | SC-001 |
| [SC-011](#sc-011) | P1 | Waiting for evidence | Recover historical industry vintages | SC-003 |
| [SC-012](#sc-012) | P1 | Done (bounded deliverable) | Measure archived final-holding exposures | SC-001 |
| [SC-013](#sc-013) | P2 | Waiting for evidence | Reconcile realized factor return attribution | SC-008, SC-010, SC-011 |
| [SC-014](#sc-014) | P3 | Waiting for evidence | Validate covariance and specific-risk forecasts | SC-013 |
| [SC-015](#sc-015) | P1 | Partial | Test incremental low-turnover information | SC-007, SC-012 |
| [SC-016](#sc-016) | P2 | Waiting for evidence | Evaluate head calibration and monotonicity | SC-003, SC-005, SC-010 |
| [SC-017](#sc-017) | P2 | Partial | Run K × weighting comparisons | SC-009, SC-012 |
| [SC-018](#sc-018) | P2 | Partial | Separate holding buffers from signal smoothing | SC-007, SC-008 |
| [SC-019](#sc-019) | P1 | Partial | Audit execution clocks and order evidence | SC-001 |
| [SC-020](#sc-020) | P1 | Waiting for evidence | Estimate matched cost scenarios and calibration | SC-008, SC-019 |
| [SC-021](#sc-021) | P1 | Partial | Predefine pressure events and controls | SC-001 |
| [SC-022](#sc-022) | P1 | Waiting for evidence | Replay frozen-cohort stress exits | SC-003, SC-005, SC-008, SC-019, SC-021 |
| [SC-023](#sc-023) | P2 | Waiting for evidence | Map capital, participation and exit capacity | SC-020, SC-022 |
| [SC-024](#sc-024) | P2 | Waiting for evidence | Audit historical financial coverage | SC-003 |
| [SC-025](#sc-025) | P2 | Waiting for evidence | Run market-characteristic ablations | SC-009, SC-010, SC-016 |
| [SC-026](#sc-026) | P2 | Waiting for evidence | Test quality and valuation incrementally | SC-024, SC-025 |
| [SC-027](#sc-027) | P0 | Partial | Draft one timestamped prospective protocol | SC-001 |
| [SC-028](#sc-028) | P1 | Done (bounded deliverable) | Specify paired inference and search accounting | SC-001 |
| [SC-029](#sc-029) | P0 | Done (bounded deliverable) | Maintain a dependency-checked task register | SC-001 |
| [SC-030](#sc-030) | P1 | Partial | Publish and maintain the evidence map | SC-029 |

<a id="sc-001"></a>
## SC-001 · Identify retained source versions

P0 · Done (bounded deliverable) · quant-market-research

Acceptance: Record hashes, dates and the distinct 86/134/136-period samples.

Next action: Preserve identities when new evidence is added.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md) · [source 2](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/low-turnover.md)

<a id="sc-002"></a>
## SC-002 · Resolve the 120-session replay discrepancy

P0 · Partial · quant-market-research

Acceptance: Recover generating code/input/support rules and reconcile 7.60%, 4.22% and 6.26% without selecting a preferred result.

Next action: Compare named replay receipts; separate recovered files from a recovered original run.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/low-turnover.md)

<a id="sc-003"></a>
## SC-003 · Certify historical membership

P0 · Waiting for evidence · quant-market-data-platform

Acceptance: Each formation membership has dated source/version, ST, listing and trading-eligibility evidence.

Next action: Audit the historical membership release and keep unresolved classifications.

Unmet gate: Archived scores alone do not certify historical eligibility.

<a id="sc-004"></a>
## SC-004 · Reconcile prices and corporate actions

P0 · Partial · quant-market-research

Acceptance: Raw/adjusted prices, shares and cash reconcile across splits, dividends and anomalous jumps.

Next action: Prioritize unresolved 2008–2016 jumps and retain unmatched events.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-005"></a>
## SC-005 · Fix missing-price and delisting treatment

P0 · Waiting for evidence · quant-market-research

Acceptance: Every selected holding remains in the ledger; unknown valuations are never silently zeroed or replaced.

Next action: Bind interval valuation and settlement policies to an auditable source release.

Unmet gate: Complete historical terminal valuations and interval coverage are not yet certified.

<a id="sc-006"></a>
## SC-006 · Specify the common timing contract

P0 · Done (bounded deliverable) · quant-market-research

Acceptance: Formation, earliest decision/execution, T+1 and valuation intervals are explicit for every comparison.

Next action: Apply the written specification only after the data and ledger admission gates pass.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-investability-protocol-draft.md)

<a id="sc-007"></a>
## SC-007 · Build matched three-arm target support

P0 · Done (bounded deliverable) · quant-market-research

Acceptance: Use one outcome-free cohort/support for benchmark, high-turnover exclusion and low-turnover selection; audit weights and missingness.

Next action: Pass retained targets and support exclusions into the ledger readiness review.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-target-support-20261128.md)

<a id="sc-008"></a>
## SC-008 · Extend the shared share/cash ledger

P0 · Partial · quant-market-research

Acceptance: Reconcile positions, cash, fees, actions, failures and terminal valuation over the admitted history using the shared provider.

Next action: Reuse the existing ledger pilot; gate extension on timing and historical inputs.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-009"></a>
## SC-009 · Compare three matched net long-only accounts

P1 · Waiting for evidence · quant-market-research

Acceptance: Same dates, eligibility, ledger, execution and cost policy; report both spread legs and benchmark-relative net results.

Next action: Run the benchmark, exclusion and low-turnover accounts only after ledger admission.

Unmet gate: Targets exist; a certified matched full-history account does not.

<a id="sc-010"></a>
## SC-010 · Version the public descriptor contract

P1 · Partial · quant-market-research

Acceptance: Document lag, unit, sign, clipping, standardization universe and coverage for each descriptor.

Next action: Separate archived proxies from newly reproducible size/beta/volatility/liquidity descriptors.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-011"></a>
## SC-011 · Recover historical industry vintages

P1 · Waiting for evidence · quant-market-data-platform

Acceptance: Formation-date industry assignments are traceable; unknown exposure remains visible.

Next action: Audit industry revisions before using dummies in attribution.

Unmet gate: Archived Top-50 industry unknown weight is material; a current classification cannot replace history.

<a id="sc-012"></a>
## SC-012 · Measure archived final-holding exposures

P1 · Done (bounded deliverable) · quant-market-research

Acceptance: Compare raw/residual scores and K on common dates using broad and local benchmarks, preserving missing descriptors.

Next action: Use the measured tail exposure reversal as a direct holding-level control requirement.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-013"></a>
## SC-013 · Reconcile realized factor return attribution

P2 · Waiting for evidence · quant-market-research

Acceptance: Lagged exposures, identified market/industry regression and account intervals reconcile contributions plus residuals; use quant-platform APIs.

Next action: Admit the base model without turnover and the extended model with turnover.

Unmet gate: Complete aligned exposure, industry and account intervals are not admitted.

<a id="sc-014"></a>
## SC-014 · Validate covariance and specific-risk forecasts

P3 · Waiting for evidence · quant-market-research

Acceptance: Estimate only from past data; test rolling forecast/realized risk, coverage and stress calibration.

Next action: Follow reconciled attribution with a separate forecast-validation experiment.

Unmet gate: An exposure diagnostic or explanatory regression is not a validated risk forecast.

<a id="sc-015"></a>
## SC-015 · Test incremental low-turnover information

P1 · Partial · quant-market-research

Acceptance: Common support/date comparisons separate low volatility, activity, illiquidity and high-turnover avoidance; retain raw controls.

Next action: Pair the three-arm accounts with ablation and control-order sensitivities.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/low-turnover.md) · [source 2](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-target-support-20261128.md)

<a id="sc-016"></a>
## SC-016 · Evaluate head calibration and monotonicity

P2 · Waiting for evidence · quant-market-research

Acceptance: Predefine mutually exclusive rank bands and horizons; report paired uncertainty and overlapping-return treatment.

Next action: Join frozen formation ranks to admitted forward labels without dropping failed holdings.

Unmet gate: The current exposure panel has no admitted forward-return labels.

<a id="sc-017"></a>
## SC-017 · Run K × weighting comparisons

P2 · Partial · quant-market-research

Acceptance: Compare a predeclared grid under matched risk/cost/eligibility and report stable regions, not a historical maximum.

Next action: Extend existing exposure-only K comparisons after net-account admission.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-018"></a>
## SC-018 · Separate holding buffers from signal smoothing

P2 · Partial · quant-market-research

Acceptance: Same signals and dates; keep net returns, target changes, real turnover and residual risk separate.

Next action: Reuse historical buffer records as development evidence and construct paired ledger cases.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/low-turnover.md)

<a id="sc-019"></a>
## SC-019 · Audit execution clocks and order evidence

P1 · Partial · quant-market-research

Acceptance: Decisions, arrival quotes, trades, fees and unfilled inventory share verified units and clock semantics.

Next action: Extend the two-date fitness review without claiming universal coverage.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)

<a id="sc-020"></a>
## SC-020 · Estimate matched cost scenarios and calibration

P1 · Waiting for evidence · quant-market-research

Acceptance: Separate fee/spread/impact/delay without double charging; scenario assumptions stay distinct from actual calibration.

Next action: Start with matched account scenarios; fit impact only if matched execution evidence is admitted.

Unmet gate: Existing quote/account scenarios do not establish broker-calibrated costs.

<a id="sc-021"></a>
## SC-021 · Predefine pressure events and controls

P1 · Partial · quant-market-research

Acceptance: Fix market/size drawdown event rules before outcomes and retain normal controls; distinguish low-ADV months.

Next action: Review and freeze the draft only after the required input, account and clock evidence is admitted; do not relabel history as prospective.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-investability-protocol-draft.md)

<a id="sc-022"></a>
## SC-022 · Replay frozen-cohort stress exits

P1 · Waiting for evidence · quant-market-research

Acceptance: Freeze pre-event holdings; retain suspensions, missing observations, unsold inventory and cash through the horizon.

Next action: Run admission checks on pre-event targets, minute data and inventory before exit simulation.

Unmet gate: Pre-event qualified holdings and aligned executable observations need admission.

<a id="sc-023"></a>
## SC-023 · Map capital, participation and exit capacity

P2 · Waiting for evidence · quant-market-research

Acceptance: Report net return, cost, unfilled inventory and exit time by capital/participation/horizon; do not equate ADV with capacity.

Next action: Use the same cost and stress-exit source revisions across the grid.

Unmet gate: Capacity depends on admitted execution and stress evidence.

<a id="sc-024"></a>
## SC-024 · Audit historical financial coverage

P2 · Waiting for evidence · quant-market-data-platform

Acceptance: Announcement-dated versions and loss/negative-equity/missing-report rules cover the intended microcap universe.

Next action: Measure coverage by date and size; retain the restricted post-2020 quality sample separately.

Unmet gate: Existing quality diagnostics mainly cover post-2020 top-800 stocks.

<a id="sc-025"></a>
## SC-025 · Run market-characteristic ablations

P2 · Waiting for evidence · quant-market-research

Acceptance: Size, turnover, volatility, reversal/momentum improve matched predictive or net portfolio outcomes with uncertainty reported.

Next action: Evaluate a small fixed family set before expanding the library.

Unmet gate: The net-account and forward-label contracts must be satisfied first.

<a id="sc-026"></a>
## SC-026 · Test quality and valuation incrementally

P2 · Waiting for evidence · quant-market-research

Acceptance: Use matched PIT coverage; separate composite quality from components and do not duplicate leverage.

Next action: Add financial families only after coverage and baseline ablation admission.

Unmet gate: Financial coverage cannot be inferred from the historical 19-factor snapshot.

<a id="sc-027"></a>
## SC-027 · Draft one timestamped prospective protocol

P0 · Partial · quant-market-research

Acceptance: Name the protocol, freeze date, models, support, allocation, costs, endpoints and amendment policy; reconcile the prior 12/24-period rules.

Next action: Review and freeze the draft only after the required input, account and clock evidence is admitted; do not relabel history as prospective.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-investability-protocol-draft.md)

<a id="sc-028"></a>
## SC-028 · Specify paired inference and search accounting

P1 · Done (bounded deliverable) · quant-market-research

Acceptance: Record every tried specification, overlapping horizons, block/HAC choice and multiplicity; no best-cell selection.

Next action: Apply the written specification only after the data and ledger admission gates pass.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/experiments/smallcap-investability-protocol-draft.md)

<a id="sc-029"></a>
## SC-029 · Maintain a dependency-checked task register

P0 · Done (bounded deliverable) · quant-market-research

Acceptance: Every task has an ID, owner, priority, status, acceptance, dependency and next action; completed items link earned evidence.

Next action: Update status only through reviewed evidence changes.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/studies/smallcap_investability/task-registry.json)

<a id="sc-030"></a>
## SC-030 · Publish and maintain the evidence map

P1 · Partial · quant-market-research

Acceptance: The bilingual site exposes priorities, current evidence, unmet gates and the next useful action with source identity.

Next action: Publish the current source-pinned snapshot; refresh when actual research gates change.

Evidence: [source 1](https://github.com/runchengxie/quant-market-research/blob/main/docs/research/factors/smallcap-style-attribution.md)
