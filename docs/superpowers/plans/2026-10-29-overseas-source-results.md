# Overseas source results documentation plan

**Goal:** Preserve the completed exploratory source audit and experiments in bilingual research notes.

**Design:** Add English and Chinese experiment notes, linking from the earlier missing-input inventory while preserving its historical content. Summaries are transcribed from external diagnostics; raw histories, manifests, predictions, acquisition scripts and detailed receipts remain external. No exporter, business logic, website selection or shared pointer changes.

- [x] Verify source acquisition QA, generating revision, manifest hashes and exact experiment sample bounds.
- [x] Document all comparisons, annual variability and comparative ETF cost/delay outcomes with limitations.
- [x] Link the chronological update and document reproduction and provider boundaries.
- [x] Validate reported numbers against external receipts; check local links, whitespace and private-path/raw-price exclusion; commit docs only.

**Review focus:** Percent versus decimal units; delayed forecast count versus simulation rows; price-index versus adjusted ETF semantics; historical availability assumptions versus observed retrieval; account-specific Alpaca feeds remain untested.

Validation: all 36 bilingual comparison rows, 24 cost rows and six manifest hashes match external diagnostics; local links and private-path exclusion pass; `git diff --check` passes; scoped overseas regression tests: 26 passed. No code changes, new tests or web build are needed for these research Markdown notes.
