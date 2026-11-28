# Small-cap investability protocol draft v0

[Chinese (Simplified)](smallcap-investability-protocol-draft.zh-CN.md)

Status: draft, written on 29 November 2026. This document specifies research choices, not a registered prospective strategy. No future allocation, production job or trade is activated. A later admission/freeze record must bind the actual input releases, implementation, allocation, cost settings and timestamp. All history already examined before that freeze remains development evidence.

## Common timing contract (SC-006)

Form signals after the final official session of each month. Use only inputs delivered by the decision timestamp; the archived 60-session turnover convention excludes the formation session. Historical delivery-time evidence is still required. The earliest order is the next official session's open; no formation-close fill is permitted. Use the source calendar, not the next available security quote, to identify that session. Record local exchange time and its UTC mapping.

All three accounts share the original cohort, finite-score support and deterministic tail policy from SC-007. Missing scores are reported before conditioning. Missing future prices, suspensions and failed fills cannot replace a selected member. The provider must retain shares, cash, receivables, unsettled quantities and failed orders. Enforce the admitted board-specific lot/limit rules, T+1 sellability and corporate-action settlement policy. No universal lot size or automatic delisting recovery is assumed here.

Report target changes, actual traded notional and drift separately. Value at each official close, retaining unknown valuations as unknown rather than zero. A monthly outcome ends at the next formation's official close; next-cycle orders start in the subsequent session. A complete observation requires all ledger intervals and terminal values to reconcile. State whether distributions, fees, taxes and interest are modeled; missing required costs block a net-return claim. Identical price/valuation/execution rules apply to all arms. Explanatory close-to-close factor attribution is separately labeled and cannot replace executable account returns.

## Pressure-event draft (SC-021)

Candidate rules are fixed here for implementation review, not selected for the best historical outcome: trigger on a five-official-session cumulative return of at most −10% for an admitted broad benchmark or at most −15% for the admitted small-stock benchmark. The thresholds are research assumptions, not calibrated risk limits. Within a source calendar, retain the first qualifying close and suppress new triggers for 20 sessions; preserve every trigger/exclusion record. The broad and small-stock benchmark must use admitted point-in-time constituents and total-return accounting.

Freeze pre-event holdings at the close immediately before the five-session trigger window (t−5 for trigger t). Exit attempts begin at the first session after t; report horizons of 5, 10 and 20 sessions, including unsold inventory, cash, unknown prices and missing quotes. No recovery-based event selection, future liquidity filter or survivor replacement is allowed. For descriptive controls, use the first session of each quarter that is not already in an active event/cooldown based on information then known; do not drop a control because its future window later crashes. These controls are descriptive, not a causal design.

ADV participation scenarios of 1%, 3% and 5% use only lagged 20-session traded value and remain uncalibrated assumptions. Do not infer a real fill from ADV alone. Event construction, matched quote/minute clocks and the inventory/valuation gates must pass before running an exit or capacity experiment. Historical evaluation under these newly written rules is retrospective. A forward event protocol can be registered only with the later freeze record.

## Evaluation specification (SC-028)

The two primary contrasts are highest-turnover exclusion minus the common-support account, and low-turnover selection minus that account. The primary endpoint is the mean paired monthly difference in net account return on the same admitted complete intervals. Report each arm, both paired differences, coverage, incomplete intervals and exclusions. Do not delete an interval in only one arm, fill an unknown return with zero or use a long-short gross spread to estimate a long-only net effect.

Predeclare HAC lag 3 and a 12-month moving-block bootstrap with 2,000 replications and seed 20261129 for uncertainty sensitivity. These are reviewable method choices, not universally correct parameters. Report 95% intervals, effective sample support and short-history limitations. Use Holm adjustment across the two primary endpoint contrasts. Track every K, weighting, buffer, window, capital and cost specification tried; additional contrasts remain exploratory unless a later independent protocol allocates a testing family before outcomes. Inspect paired differences and stability regions, not the best grid cell. Overlap at different return horizons requires revisiting the dependence specification before inference.

## Prospective admission draft (SC-027)

The old 12- and 24-period rules remain historical. For this proposed new protocol, 12 completed monthly intervals is a descriptive checkpoint and 24 is the earliest planned primary evaluation checkpoint; neither count proves significance. Do not stop early after favorable results or count reviewed historical/later-observation months as new prospective evidence. The first prospective formation must occur after the actual freeze timestamp and data admission, with an outcome interval starting afterward. That timestamp does not exist yet.

Admission requires SC-003/004/005 historical/data rules, SC-008 reconciled accounting, SC-019 clock evidence and explicit cost assumptions. Freeze the final descriptor transformations, cohort, tails, optional K/buffer rules, benchmark, provider revisions, cost scenarios, return endpoints and amendment policy. Amendments create a new named version and retain the prior record; results before and after incompatible amendments are not pooled. Publish every admitted interval even if performance disappoints. No scheduler is installed by this draft.

This draft advances timing/evaluation specification and narrows pressure/forward choices, while leaving data, ledger, actual registration and execution gates open. See the [task register](../../../studies/smallcap_investability/README.md).
