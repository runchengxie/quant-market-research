# Asset-return study validation

Reviewed frozen calculations: `e718b5b`; input preparation: `81e5e4f`. The reviewed public projection records exact input, metadata, analysis, runner and result hashes. A subsequent runner correction sorts reverse/shuffled CSV rows before applying elapsed annual drags; frozen inputs were chronological and their numerical results are unchanged.

Independent read-only review reconciled the public projection with all four frozen runs and found no raw-data leaks. It identified the reverse-order cost bug. A failing counterexample reproduced +2.0408% instead of -2% for a constant-price one-year sample; the regression now passes after chronology normalization.

Validation against target `61d176ed7e63f4fd5da157b89cfc4bedd878b612`, including its platform API migration, on task revision `b304f69`:

- `uv run --locked --extra duckdb --extra dev pytest -q`: 896 passed, 22 skipped. Skips require the optional formal/integration providers and are not claims of validated execution calibration.
- `uv run --locked --extra dev ruff check src tests scripts`: passed.
- `git diff --check`: passed.
- Web `npm test`: 314 passed. The existing Node spawn configuration tests required execution outside the restricted subprocess sandbox (`EPERM` inside); no tests were disabled.
- `npm run build`: passed, 60 static pages; `npm run verify:static`: passed, including forbidden private paths/credential markers.
- Browser checks on task port 54831: 15 passed, covering new evidence at 320/1280 widths in both languages and existing cash-flow navigation, hydration and no-JavaScript routes.

The browser test expectation was extended for the new navigation item. The initial old expectation failed with four expected versus five actual links; the rerun passed without changing navigation behavior to conceal the added item.

This is evidence for descriptive calculations and presentation, not independent authentication of original financial vintages, actual cash-entitlement accounts, calibrated execution costs, future loss probabilities or commercial data redistribution rights. Those limitations remain visible in the findings and topic section.
