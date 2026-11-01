# Decision-risk evidence validation

Base revision `7b8ab68b78e1c495604d19b3788fedb82a9619c3`; calculation/reader implementation revision `f15880ab29be279039149623a200345ff1b3513e`. Subsequent validation prose and the legacy browser-selector correction do not alter calculation bytes. This extends the existing asset-return topic; earlier artifacts and the prospective protocol remain unchanged.

## Retained evidence and exact scopes

- Authoritative full result: external research task `asset-decision-risk-20261101/run-03/results.json`. The public `asset_decision_reviewed.json` records its exact digest, all study-module/runner hashes and the conclusion-register hash. Prior runs are preserved. Per-window spending records and monthly ETF marks are not projected.
- Data-owner task with the same ID retains three official CSI PDF factsheets, early ETF response/retry receipts and sovereign-yield access probes. Early ETF gaps at the exact2012-11-30 session are not filled. Direct retries leave510300 NAV and159919 close unavailable; these products explicitly retain their mature reviewed samples.512100 admits the complete monthly extension from2016-11-30. Month-end verification does not certify every daily quote.
- All three documented `yc_cb` window probes returned40203. Raw responses are hashed and checked against receipt codes. No actual sovereign-yield-increase condition is admitted, and no credentials or permissions were changed. Bond-negative-return stress stays separately labeled.
- First-round CSV hashes are checked against their own frozen runs; mature fallback ETF results are checked against the public reviewed follow-up digest and recomputed accounting. Source PDFs are hash checked and their publication dates were read from issuer text. Publication belongs to the price-index families; original total-return vintages remain uncertified.

## Verification

- Full Python suite at implementation head: **923 passed, 22 optional provider/integration skips**.
- Focused study regressions: **9 passed**, covering paired block reproducibility, policy parity with the existing allocation engine, funded cash, CPI-indexed demand, shortfall accounting, sequence effects with withdrawals, small stress samples, censored/tied-peak recovery, publication boundary, per-side fees, evidence-stage guard and projection boundary. Several assertions share one test case.
- Ruff and `git diff --check`: passed.
- Web unit suite: **318 passed**. Production Astro build, reviewed-file hash lock and public static verification passed; built bytes match all four public datasets.
- Initial complete Chromium run: 282 passed and 4 legacy table-count assertions failed after the new child tables were added. The selector was scoped to the original module’s five tables; all 9 affected old/new evidence cases then passed, including 320px and no-JavaScript coverage. Full suite reruns/CI remain required release gates.
- The two new Chromium cases passed at1280px and390px, including both locales, scenario controls, nine visible rows per selection, public download schema and viewport width. Complete browser/required remote checks are executed as release gates; final results live in the PR and external closeout rather than being inferred from this record.
- Independent review matched the public projection, full-result digest, every calculation hash and register. A separate asset-level simulator reproduced **all11,664 spending windows**, including terminal real capital, paid/unmet demand and first-shortfall month. It found one important prose correction: relative geometric CAGR depends on sampled composition/era, not on reordering identical paired observations. Both opening paragraphs were corrected; the implementation already used the correct compounding. No other material issue was found.

The reviewer did not certify supplier accuracy, original total-return vintages, actual execution or browser behavior. These remain explicit boundaries; browser checks are performed by the implementing task.

## Reproduction

Resolve configured project roots explicitly. Use `scripts/run_asset_decision_study.py --help`, supplying:

1. First-round research task `asset-returns-20261031` and its data-owner task.
2. Data-owner task `asset-robustness-20261031` and reviewed research `run-02` from that task.
3. New owner task `asset-decision-risk-20261101` and a fresh external output directory.

The runner never fetches APIs, moves shared aliases or creates prospective observations. Projection uses `scripts/project_asset_decision_summary.py --source .../results.json --output ...`; source artifacts enter the website only after review and release-manifest update. Keep the lockfile/runtime versions with the external closeout.

## Interpretation

Resampling percentiles and positive fractions condition on observed history and block rules; they are not future probabilities or multiple-testing-adjusted evidence. Historical spending frequencies use overlapping complete windows, include failed accounts and are not lifetime safe-withdrawal estimates. Stress conditions are contemporaneous descriptions; inflation labels inherit rounded CPI input limitations. Launch-period comparisons do not identify causal backfill bias. Fees are hypothetical per-side sensitivities, not calibrated account returns. The separate prospective protocol remains unadmitted, with zero completed windows.
