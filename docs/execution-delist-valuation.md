# Nontrading valuation scenarios for delisted holdings

[中文](execution-delist-valuation.zh-CN.md)

These opt-in scenarios investigate sensitivity to declared delisted-asset valuations. Valuation events preserve legal shares, create no cash or fills, and permanently prohibit continued A-share trading for affected instruments. The default path still rejects unsupported held valuations.

Source packets bind source hashes, normalized facts, native quotes, the study window and its actual session calendar. Raw prices, adjustment factors, suspension records and modeled corporate actions remain unchanged. Later funded targets are recomputed after declarations; post-hoc NAV patches are insufficient.

## Scenario boundaries

`full_impairment` and `impairment_then_observed` require the exact delisting date to be known by 09:00 on that date. This availability is unproven for 000982, so those strict scenarios remain rejected.

Two alternatives explicitly impair at 09:00 on the first session after the termination decision became publicly available: June 24, 2024 for 600321 and August 5 for 002621 and 000982. Some impairments precede legal delisting. This is a conservative assumption, not a fair-value conclusion or proof that the exact delisting date was then known.

- `termination_decision_full_impairment`: retain zero valuation and legal inventory thereafter.
- `termination_decision_impairment_then_observed`: subsequently value inventory using available historical successor-board quotes, without reopening trading or crediting cash.

The 183 native daily quote rows remain single-source candidates without independent historical-price or official volume/amount-unit verification. MyGym's transfer-date facts are retrospectively supported by an annual report published in 2025, not established as 2024 decision-time evidence. All scenarios retain `revision_safe=false` and these limitations.

Quote availability is assumed to be 09:00 on the next calendar day. Effective recognition moves to the first subsequent study session at 09:00, preserving the original availability timestamp. Weekends and holidays create no additional daily ledgers. Quotes available after year-end are excluded. When multiple quotes map to one effective instant, use the latest already available quote. Never backfill an unknown interval from a future quote.

## Running and reviewing

Use a new external output directory and hash-verified immutable prepared inputs. Do not reuse prior simulation outputs. Two pilots leave the nine-scenario matrix incomplete and unpublished.

```bash
uv run --locked --extra formal --extra duckdb python scripts/run_execution_cost_minute.py \
  --run-prepared --output "$PREPARED_OUTPUT" \
  --valuation-source-packet "$SOURCE_PACKET" \
  --valuation-mode termination_decision_full_impairment \
  --scenario fees_1m --scenario fees_10m
```

Run the observed-quote alternative in a separate new directory. Changed policy, inputs, sources or implementation fingerprints prohibit resuming completed results. Each scenario retains its valuation ledger and policy receipt separately from corporate entitlements and cash executions.

Independently reconstruct cash, shares, fees, record-date entitlements, daily NAV and valuation events. Confirm no affected fills after declarations, fabricated zero-price bars or disposals. Complete ledgers establish closure under a stated assumption, not realized recovery, resolved strict annual valuation or live capacity. Successor-board disposal requires separate custody/confirmation, auction, fee and liquidity modeling.

The original 18 published scenarios remain unchanged. Strict full-2024 failures remain retained; these alternatives do not replace them.

## Current experiment scope

Both termination-decision alternatives ran CNY 1m and CNY 10m pilots covering 242 sessions each. Independent reconstruction found no accounting errors or affected fills after declarations. Valuation-event cash changes were zero and legal inventory remained retained.

This establishes ledger closure only under the stated assumptions. Each policy has two of nine matrix scenarios and remains unpublished as a complete matrix. Single-source quotes, revision-vintage and actual-disposal evidence limitations remain.
