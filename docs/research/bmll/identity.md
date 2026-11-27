# Historical identity reconciliation

[简体中文](identity.zh-CN.md)

Run the coverage audit before expanding the quote sample. Then examine dated reference rows for failed matches and changing identifiers. `scripts/audit_bmll_identities.py` accepts a retained statement response, explicit `--symbols`, explicit `--dates` and a new external `--output`. It decodes transport booleans strictly, rejects duplicate listings, preserves the full requested grid and flags changes between adjacent uniquely active snapshots. Missing or ambiguous snapshots break the comparison chain.

A sampled transition only locates an interval. It does not establish an event date, successor security or adjustment factor. Do not join a ticker across time without checking instrument identity. The same ticker may describe different issuers, while a reverse split may change identifiers without changing the ticker.

## Reconciliation record

Keep provider observations private. For each unresolved case, retain the reference identifiers and a separate primary-source event record with issuer, announcement date, effective date, event type, old/new public security identifiers, ratio or cash consideration where relevant, source URL and reading scope. Separate a trading suspension from formal delisting and cash settlement. Announcement terms still require a ledger and fractional-share treatment before computing returns.

The first follow-up uses four sampled dates and a fixed queue derived from the prior cohort. It checks issuer announcements and exchange notices for reverse splits, cash acquisitions, ticker changes and listing departures. Some missing reference cases remain unresolved. It does not automatically relabel missing quotes as feed failures, fill absent returns with zero, or certify historical common-stock eligibility.

Next, query immediately before and after a documented effective date and reconcile public identifiers. Audit the underlying historical feature source as well: a stale ticker or OTC/partnership instrument in that source can invalidate an exchange-listed common-stock selector even when the market-data query works correctly.
