# First-round validation and reproduction

Read the [English findings](findings-20261107.md) or [Chinese findings](findings-20261107.zh-CN.md) before interpreting the aggregate. This record distinguishes numerical completeness, source identity, independent point checks and still-unresolved investment-account semantics.

## Frozen data and code

The analysis code is pinned to `44ffeed` (the full source revision and code-file hashes are retained in run results). The aggregate records three exact manifest hashes, three result hashes and the projector file hash. Manifest paths are machine-local and never projected. Supplier data and full results remain outside Git.

Resolve `DATA_OWNER_TASK` to the data owner's `tasks/commodity-equity-20261107` and `RESEARCH_TASK` to the research owner's `china_commodity_equity/round1-20261107`, both below their configured project data roots. Never derive permanent data paths from a task worktree. The owner task retains the acquisition recipe and bounded query JSON, raw responses and receipts, the original publisher PDFs and their URL/hash receipts, plus the four targeted empty gap probes. The equity history is referenced from `asset-returns-20261031` receipts rather than copied or modified. Its source catalog identifies `H00300.CSI` as the CSI 300 return index, `H00985.CSI` as CSI All Share total return and `H00852.CSI` as CSI 1000 total return.

The commodity acquisition comprises seven bounded 2025 probes and 83 history/calendar requests. History covers seven commodity indices in three-calendar-year chunks plus 2026, four 2026 equity index responses, and separate SSE/SHFE open-session calendars. All 83 requests returned code zero; ten early sector-history batches were empty. Successful transport is not a claim of complete history. Reported values are recomputed from close ratios; supplier `pct_chg` is not used.

Private bundle schema:

```json
{
  "schema_version": 1,
  "source_revision": "exact committed analysis revision",
  "start": "2006-12-29",
  "end": "2025-12-31",
  "sources": [{
    "receipt_path": "owner receipt location",
    "receipt_sha256": "exact receipt hash",
    "ids": ["selected response identifiers"]
  }],
  "series": {
    "H00300.CSI": {"role": "equity", "currency": "CNY", "return_basis": "total_return"},
    "NHCI.NH": {"role": "commodity", "currency": "CNY", "return_basis": "commodity_futures_return_index"}
  }
}
```

Every selected receipt response is hash-verified. Nonzero or empty responses remain in receipts and do not become observations. Quote dates, positive finite levels, per-response series identity, duplicates and calendar membership are checked. Each pair checks its full own calendar within its observed overlap before selecting common sessions. Calendars are supplier-reported exchange calendars, independent of the quote series; they are not independently certified publisher histories. Missing sessions block that pair, with no forward filling or zero returns. A calendar extending into a later month certifies earlier final-session endpoints; its truncated terminal month cannot be called complete merely because its last observed session is present.

The full attempted overlap, explicitly shorter baseline and recent panel use separate manifests and new output directories. Full-history comparison of four long commodity series remains blocked by January 26–27, 2006. CSI All Share has an additional August 2, 2011 gap. The 2006 year-end baseline was chosen after coverage audit, before interpreting its performance; it is a sample restriction rather than restored 2004 history. Sector starts are separately reported.

## Reproduce numerical runs

Use the retained `historical-reviewed-manifest.json`, `baseline-reviewed-manifest.json` and `recent-reviewed-manifest.json`. A later acquisition creates a new observation vintage. For each panel, run the pinned analysis revision with a new output name:

```bash
uv run --locked --extra dev python -m market_research.studies.commodity_equity.run \
  --manifest "$RESEARCH_TASK/baseline-reviewed-manifest.json" \
  --output "$RESEARCH_TASK/baseline-reproduction-NEW"

uv run --locked --extra dev python scripts/project_commodity_equity.py \
  --full "$RESEARCH_TASK/historical-reviewed/result.json" \
  --baseline "$RESEARCH_TASK/baseline-reviewed/result.json" \
  --recent "$RESEARCH_TASK/recent-reviewed/result.json" \
  --output "$RESEARCH_TASK/public-projection-NEW.json"
```

The runner refuses existing output directories and repository-contained outputs. A moving `current` or `latest` alias is never updated. Results include generation time, so a fresh result hash is expected; compare numerical fields and frozen input/code identities. Reproduce a published result byte hash from the retained exact artifact, not a newly generated timestamp.

## Independent checks and review

- Thirty allocation terminal wealth values were recomputed independently from period-end weighted price growth products, rather than the runner's daily drifting holdings. Maximum absolute wealth error was `2.49e-14` against tolerance `1e-11`. The task retains `independent-check.json` and its reproduction recipe.
- Seven 2025-12-31 index closes matched the original publisher PDF at the stated 0.01-point precision. The PDF was visually inspected. This does not validate the complete path, historical revisions or a natural-year return. The ARR field is annualized and has not been reconciled to calendar endpoint growth.
- Independent code review found stale last-month reporting, exclusion of weekend month ends and absent fixed 3/5/10-year comparisons. Regression tests reproduced each, then passed after the fixes. A second review found missing public return-basis metadata; the projection now preserves pair identities, currency and return basis without private receipts.
- Tests cover hash tampering, mixed identity, duplicate/invalid quotes, missing sessions, exchange-calendar differences, initial weights and drift, monthly/annual rebalancing, cost drags, censored recovery, exact month ends, missing windows, recent/fixed endpoints, external output boundaries, end-to-end runs and the private-metadata projection boundary.

## Validation outcome

Local checks on the final analysis and projector passed: 952 Python tests, with 22 skips for optional formal/integration providers; all 332 web tests; Ruff; Astro build; static publication-boundary verification; local topic links, JSON parsing and evidence hash bindings. The separate remote execution-provider job is required before merge. Existing unrelated React key/deprecation and Python warnings are not treated as new failures. Final independent review found no remaining important issues.

## Open gates

The source data contract's complete methodology, collateral, fee and publication-rights receipts remain acceptance requirements for investable-account publication. This round publishes only manually reviewed derived descriptive statistics. It grants no supplier raw-data redistribution rights. An eight-session introductory roll description conflicts with the five-session detailed rule in the 2025 PDF; historical methodology versions have not been recovered. ETF/CTA implementation, release-vintage macro regimes, inventory/warehouse-receipt factors and causal sector attribution remain untested. The existing asset-return release manifest and reviewed payloads are unchanged.

Sources: [Tushare commodity-index endpoint and codes](https://tushare.pro/document/2?doc_id=468), [Nanhua 2025 methodology](https://www.nanhua.net/cmsbigfile/2025/05/a3eb91a3-d6fc-4d71-b652-d55a60e0b10d/南华商品指数——编制细则(2025).pdf), [Nanhua year-end report](https://www.nanhua.net/cmsbigfile/2025/12/4cab9e74-e023-4099-9fcf-bd31c7549b5a/南华商品指数日报20251231.pdf).
