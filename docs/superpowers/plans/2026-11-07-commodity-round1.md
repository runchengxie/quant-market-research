# Commodity and equity first-round research implementation plan

**Goal:** Turn the registered protocol into a reproducible coverage audit and the first defensible common-sample comparison.

**Architecture:** Preserve supplier responses and acquisition recipes under the data owner's task directory. Research consumes hashed frozen responses through a study-local reader. Publish only reviewed aggregates and clear unresolved evidence; preserve the existing asset-return release.

**Tech stack:** Python, pandas, pytest, JSON receipts, existing Astro Markdown routes.

**Spec:** `docs/research/asset-returns/china-commodity-equity.md`.

## Constraints and review focus

- Do not read credentials into logs, copy raw data into Git, change shared data aliases, or modify production.
- Missing or denied endpoints must remain explicit; annual chunks must not silently truncate.
- Validate independent trading calendars, internal gaps, month-end endpoints and mixed series identities.
- Total returns, commodity index returns and investable account returns remain separate.
- Portfolio returns use beginning weights and drift between actual rebalance dates; costs are labeled hypothetical.
- Unrecovered episodes remain censored; incomplete months and missing holding windows cannot become complete results.

## Tasks

- [x] Acquire a bounded endpoint probe using existing private configuration loading. Freeze responses, request parameters, retrieval times and hashes under the data owner. Inspect methodology and publisher cross-check sources.
- [x] Add failing synthetic tests in `tests/studies/test_commodity_equity.py` covering hash integrity, duplicate/invalid data, missing calendar sessions, monthly endpoint selection, compounding, drift/rebalancing and recovery censoring. Run them to confirm failure, then implement `src/market_research/studies/commodity_equity/{inputs,analysis,run}.py` with a frozen-input CLI and external output requirement.
- [x] Acquire annual data batches only for usable sources; reuse existing owner equity/calendar receipts by reference when appropriate. Run the audited analysis, retain unresolved semantic/coverage checks and independent reconciliations.
- [x] Update bilingual topic documents, benchmark identities and conclusion register with reviewed aggregates or explicit blocking evidence. Add reproducible commands and source receipts without raw data or local machine paths.
- [ ] Run relevant Python and web checks, review the whole diff, commit, push, create PR and merge only after remote checks pass against current main. Clean only this task's branch/worktree.

All steps execute inline under the user's request to advance the remaining work. Independently review the completed implementation before publishing.

Validation before PR: 952 Python passed /22 optional-provider skips; 332 web passed; Ruff, Astro build, static boundary and evidence bindings passed. Independent code and evidence review complete; calendar and public return-basis findings resolved. Remote checks and merge remain pending.
