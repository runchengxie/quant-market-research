# Interactive reading validation

The change adds ten charts over the existing reviewed public data and revises reader-facing Chinese prose. No financial source values, evidence stages or original archived report bytes change. The editorial report is edition 1.0.10.

## Scope

The source audit covers 272 website source files and 38 registered documents. It checks Chinese prose for the owner's prohibited rhetorical patterns, punctuation, long clauses and repeated possessive constructions. It excludes lookup keys, executable code, attributed quotations and sealed datasets. The rendered audit opens all 61 generated HTML routes in both locales, for 122 visits. Its visible heading, paragraph, label and disclosure-summary checks report zero remaining issues. These mechanical checks support the manual wording review; they do not establish that every reader understands every passage.

The charts retain source windows and assumptions. They display summary observations already published by the research. They do not synthesize daily paths or present resampling outcomes as forecasts. Source tables remain accessible without scripts. Endpoint and ETF tables include every reviewed observation and filter to the selected controls when scripts run. Interval medians appear in the table and accessible chart summary.

## Checks

- Python suite passed 923 tests, with 22 optional dependency skips. Ruff passed.
- Website suite passed 327 tests. Focused chart, source-note and prose regressions passed 11 tests.
- Production build, static-site verification and reviewed asset release hashes passed.
- New chart browser checks passed all five cases, covering both languages at 320 and 1280 pixels and disabled JavaScript.
- Independent whole-branch review found two missing numeric-table/accessibility cases. Both were fixed, and follow-up review found no remaining actionable issues.

Full browser validation and required remote checks must pass before merge. Detailed runtime logs, route records and screenshots are retained under the owning project's external task data directory with task identifier `interactive-reading-20261101`.
