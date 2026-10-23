# Frozen research reproduction baselines

These completed snapshots are intentionally retained for reproduction. Their
research/navigation deliverables were published through [PR #223](https://github.com/runchengxie/quant-market-research/pull/223)
(merge `fff37dd51ba7889cdbea0a598fb64e2aa1dd6cac`). They are not unfinished
implementation tasks and are not candidates for automatic cleanup.

| Baseline | Source revision | Preserved worktree relative to `CODE_ROOT` |
| --- | --- | --- |
| Grouped valuation | `05a15ea27151ef5772f9aeacecf52e0efffe9031` | `.worktrees/quant-market-research-grouped-valuation-20261021` |
| Topic navigation | `e3f0f1c103e106da5cd97494126fb277f746549e` | `.worktrees/quant-market-research-topic-navigation-20261021` |

Purpose: retain the delivered source snapshots and a recovery path for reproducing
historical research and navigation acceptance. Custody rests with the workspace
owner. The original agent and an operational custodian/contact have not been
established; this record does not assign or invent either identity.

Runtime dependencies are defined by each source revision's `pyproject.toml` and
`uv.lock`, and its `web/package.json` and `web/package-lock.json`; use those frozen
files rather than the latest main branch or an existing mutable environment.
Both Python locks require Python 3.11 or newer and retain the formal provider
pins: runtime `4fbfe973540e15fb6552068be037229d2f53d540`, platform and research
contracts `15ec62b66e894395d694049eaaace931de4a1265` (formal execution requires
Python 3.12 or newer). Browser reproduction also requires the Playwright browser
matching the snapshot's Node lock. Both snapshots lock pandas 3.0.5, PyArrow
25.0.1, DuckDB 1.5.5, and NumPy 2.4.6 (Python below 3.12) or 2.5.3
(Python 3.12 and newer), plus Astro 7.3.2 and Playwright 1.63.0.
Do not upgrade these preserved environments
as part of routine maintenance; reproduce in a separate temporary environment.

Grouped valuation's retained acceptance artifacts are owned under
`DATA_ROOT/quant/quant-market-research/task_outputs/grouped-valuation-20261021`.
The October 24 closeout rehashed all 18 receipt-bound artifacts with zero
mismatches. The publication cleanup record explicitly preserves both original
worktrees. Full receipts and the closeout evidence remain local; this document
copies no private source, raw data, result metrics, credentials or local paths.
These preservation facts do not establish machine-wide inactivity or prove that
no runtime consumer still references a snapshot.

Retirement condition: the workspace owner first inventories and verifies the
absence of runtime/scheduler/downstream references, confirms that the source and
retained evidence provide a usable recovery path, and explicitly retires the
baseline. Until then, preserve the worktree and its unique ignored files. Neither
age, patch equivalence, a merged publication, nor this record authorizes deletion.
No automatic cleanup applies to these baselines.
