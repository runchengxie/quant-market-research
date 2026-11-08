# Third exploration validation

The [English report](next-20261108.md) and [Chinese report](next-20261108.zh-CN.md) present the same frozen derived values. [Evidence binding](next-evidence-20261108.json) records the summary hash and independent check recipe. Numerical source hashes are checked by an automated regression test.

- Six focused tests cover future-price perturbations, integer lots, both roll legs, final exit costs, margin rejection, missing interior roll dates, capture metadata contradictions and source hash bindings.
- Independent contract segment endpoints reconcile CNY 76,110 gross P&L, 212 traded lots, CNY 318 exchange fees and all three terminal equity values exactly. Five risk-control CAGRs independently reconcile to elapsed dates and terminal wealth.
- DCE calendars are checked against the frozen SHFE calendar for the trial range. Each held contract must cover all required sessions. Price and settlement-parameter marks agree; no fee unit is guessed for percentage charges.
- Macro raw/receipt hashes and seals are verified. Public row counts, periods and retrieval times are derived from the verified payload rather than trusted from a separate index. Contradictory metadata is rejected.
- Full local Python suite passed with 968 tests and 22 optional-provider skips; seven existing warnings remain. Ruff and `git diff --check` passed.
- Website suite passed with 333 tests. Astro build and static-site boundary checks passed. No raw supplier rows or private machine paths enter the page.
- Two browser tests passed at 390px and 1280px. They cover chart initialization, holding-period/weight/rebalancing selectors, source counts, language switching, saved choices, base-path links, scope notices and horizontal page overflow. Screenshots were inspected outside Git.
- Independent review found two important validation gaps, both repaired with regression coverage. Re-review found no remaining important issue.

The tests certify the calculations and presentation within the stated model. They do not certify executable settlement fills, historical macro vintages, future diversification benefits or a running macro collection schedule. Remote required checks and the merge identity are recorded in the pull request rather than invented in this source-bound local record.
