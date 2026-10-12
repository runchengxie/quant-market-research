# Local data audit and release gate

The first three-day local source audit and static measurements are complete; see pilot_findings.md. No actual-order calibration or dynamic-impact identification is complete. The owner confirmed aggregate publication permission on 2026-10-12. Reviewed static aggregate statistics are public; raw sources, per-security measurements and actual orders remain private. Historical deal special-event percentages were not revalidated by this snapshot-only study.

Before a pilot, resolve configured workspace roots and the authoritative market-data platform dataset. Inspect its manifests, symlinks/current aliases, schema, exchange coverage, security/date coverage and quality reports read-only. Do not move data or rerun ingestion as part of presentation work.

Require snapshot timestamps with exchange/time-zone semantics, ten bid/ask prices and quantities with validated price/share units, session classification, corporate-action context, and sequence fields where available. For orders/trades, document event types, exchange-specific identifiers, cancellation links and zero-price semantics. Quarantine ambiguous records before trade-direction or impact estimation. Require point-in-time market cap, lagged turnover/ADV and volatility inputs for grouping.

A sample manifest must state provider/version, date/security selection, input hashes, fields/units, exclusions and gate outcomes. Include large/mid/small stocks and several states only when data coverage permits; do not claim representativeness from convenience selection.

Store raw data, orders and generated results under the configured external data root for the owning project. Share data through its explicit asset contract. This repository stores code, protocol and reviewed aggregate derivatives only. Check supplier redistribution terms before publication; report suppressions and coverage limits. Public cost surfaces require benchmark, side, order-size grid, coverage fraction, group counts, quantiles, uncertainty and validation-period metadata. No such surface is currently published.
