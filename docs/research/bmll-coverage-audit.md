# Historical identity before quote analysis

[简体中文](bmll-coverage-audit.zh-CN.md)

Use `scripts/audit_bmll_coverage.py` to check a fixed retrospective candidate cohort across explicit dates. Missing reference rows and inactive or ambiguous identities stay in the denominator. The query joins NBBO only when exactly one active `@SIP` listing is found for that date and ticker.

Generate SQL with `--candidate-report`, `--dates` and a new external `--output`. Execute it through `scripts/run_bmll_query.py` on an existing authorized warehouse. Summarize with the same arguments plus `--response` and `--executed-sql`. The summarizer checks the retained SQL against the requested cohort and requires a complete, untruncated result grid. Keep SQL, responses, input hashes and findings under the project data root. Never publish security-level vendor results.

The session filter uses New York local time from 09:30 inclusive to 16:00 exclusive. Choose full sessions explicitly; this is not a holiday or early-close calendar. First/last timestamps are local wall times returned by SQL conversion, even if the statement transport appends a timezone marker. Price-valid counts require a positive bid and ask at least as high as bid. Locked quotes are included. These counts do not measure quote age, executable size or time-weighted coverage.

## What to resolve next

A missing row is a mapping or coverage question. An inactive record is a historical identity question, not sufficient proof of delisting. Ticker changes, share classes, mergers and splits require dated identifiers and corporate-action records. Track listing-ID changes within each ticker and retain every original candidate. Modern vendor snapshots may contain later revisions.

Before a larger stress study, form cohorts before the event, match capitalization and prior trading activity, and retain subsequent departures. Register the comparison window and thresholds before observing outcomes. Estimate fresh-quote spread and displayed bid dollars jointly, with stale/invalid time reported separately. NBBO cannot recover queue position or the full order book.

For portfolio work, reconcile cash and share ledgers through corporate actions before claiming returns. Compare buffered ranks with fixed ranks using actual trade turnover and costs. Financial quality groups require filing-time availability, historical shares and restatement handling. Cross-market comparisons should use common within-market ranks and preserve local trading rules.

The three-date pilot is exploratory. Its selected dates are not an independent confirmatory sample. Query success is not historical universe certification or investment performance.
