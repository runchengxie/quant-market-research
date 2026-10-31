# Asset evidence closure validation

Calculation and implementation revision: `5524685ac973ac10fe99e3a258670f9852b00e47`, based on `2ca12cfb0d6623946b3aee9194790e17cd5c549d`. The following documentation-only commit does not change calculation bytes. PR: <https://github.com/runchengxie/quant-market-research/pull/248>.

## Verified evidence

- Authoritative external audit: research task `asset-evidence-closure-20261031/run-02/results.json`. The public projection records its full SHA-256 and calculation file hashes; all match the reviewed source. Run-01 remains preserved, superseded only for provenance after a comment was finalized.
- Data-owner task with the same ID retains raw receipts, bounded retry receipts, explicit-field listing masters, 44 unique FY2025 income probes, name histories, index probes, acquisition recipes and issuer PDF/source hash. Failed transport responses remain visible. Only the successful source records used by the calculation are claimed as verified.
- The income component is manifest-hash checked. Existing normalized history remains reconstructed before its actual observation period; no original financial-vintage certification is introduced.
- Independent final review found no important or critical issues, checked all 46 referenced owner response hashes and public projection/result/code consistency, and reran the focused tests (11 passed).

## Local validation

- `uv run --locked --extra duckdb --extra dev pytest -q`: **914 passed, 22 optional integration skips**. Provider-dependent integration gates run separately in CI.
- `uv run --locked --extra dev ruff check src tests scripts`: passed.
- `npm test` in `web`: **318 passed**.
- `npm run build:pages`: Astro checks/build and public static boundary verification passed, including the new asset/protocol hash gate.
- The two new Chromium acceptance cases passed at 1280px and 390px: English/Chinese, both cost bases, unadmitted forward status, strict ETF mismatches and aggregate download boundaries. Complete browser suite and remote required checks are also executed; final statuses are retained in the external closeout and PR checks, without inferring deployment from a source merge.
- Historical update-gate exercise: 252 to 253 existing monthly observations, one appended month, unchanged overlap, `published=false`; receipt includes hashes of the exact parsed bytes and gate code. This is a replay test, not a new observation or admission.
- `git diff --check`: passed.

## Reproduction

Resolve configured roots first; the settings file does not export shell variables. All run outputs belong under the configured research data root, while original API responses remain with the data owner. Inspect each CLI's `--help`:

```sh
uv run python scripts/audit_asset_evidence_closure.py --help
uv run python scripts/project_asset_closure_summary.py --help
uv run python scripts/validate_asset_update.py --help
uv run python scripts/register_research_window.py --help
```

Supply the explicit owner task, cohort owner task `asset-robustness-20261031`, manifest-sealed normalized fundamentals and prior `run-02/512100_SH_monthly.csv`. Select a fresh output file. Project the reviewed closure aggregates only after reconciliation; changes to any public evidence or protocol require deliberate release-manifest review. No command moves a shared latest alias or schedules a production task.

The field semantics were checked against [TuShare stock_basic](https://tushare.pro/document/2?doc_id=25) and [income](https://tushare.pro/document/2?doc_id=33). Observed coverage is specific to the configured service route; a successful empty response does not prove universal absence from all vendors. The issuer source is linked in the findings, with the PDF retained privately.

## Pending evidence

Corporate-action continuity, exact historical share ledgers, original financial revisions, quantitative ETF cause attribution and the 2018/2019 NAV discrepancies remain unresolved. The prospective protocol is publicly committed and has independent GitHub CI server-time evidence binding that revision; this proves protocol publication only. Real November baseline, pre-entry receipt, its own independent time evidence and admission review remain future requirements. No prospective outcomes have been fabricated.
