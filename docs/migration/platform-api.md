# Public platform imports

Production Python callers use the portfolio, analytics, and backtest owners in
`quant_platform`. The compatibility namespace remains available for historical
callers and existing compatibility tests. This migration changes import ownership;
portfolio policies and persisted artifact identifiers retain their existing meaning.

`tests/test_platform_import_boundary.py` prevents new production imports from the
compatibility namespace in `src` and `scripts`.

The pinned runtime contract predates the optional `sell_round_lot` setting.
The runtime adapter omits this field only when its value is `None`, preserving
the existing request format. It rejects an explicit sell lot setting with an
error until the runtime supports that policy; it never silently drops the rule.
