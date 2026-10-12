# Execution evidence and interactive presentation plan

**Goal:** Implement the approved cost-topic chart redesign, early Shenzhen replay fitness audit, bounded dynamic execution counterfactuals, and a real-order research calibration entry.

**Architecture:** Reuse reviewed public aggregates for the charts. Keep vendor normalization with the data platform and general simulation with quant-platform; this topic adds research diagnostics, benchmark alignment and validation protocols. Event semantics and source ordering are gates, never inferred from match rates. A snapshot-path experiment may measure counterfactual replenishment sensitivity but cannot identify causal own-order impact or queue fills.

**Constraints:** Bilingual locale catalogs, mobile width320px, missing values distinct fromzero, reviewed aggregates only, all raw/per-order outputs external. Actual, paper and synthetic evidence labels cannot be interchanged. No new actual trades or broker actions.

## Tasks

- [x] Interactive chart controls for date, side, size, group and metric; compact capital/scenario comparison. Full tables folded, useful non-JavaScript fallback, static export figures retained. Unit and browser tests for mapping, missingness, locale and responsive layout.
- [x] Replay audit of saved early Shenzhen orders/trades: event dictionaries, cancellation and identity accounting, ordering and initial-book coverage; explicit unproven gates. Source-backed aggregate run, conservation/error tests, reproduction protocol.
- [x] Dynamic execution research on bounded eligible paths only: market/TWAP/participation/limit assumptions, quote availability, depth depletion and opportunity-cost accounting; declare proxy replenishment, unidentified queues and no causal impact. Use existing provider/engine where available; disclose unsupported scenarios rather than invent fills.
- [x] Real-order entry with explicit canonical orders/fills/quotes and actual/paper/synthetic provenance. Validate IDs, parent relationships, terminal state, quantities, timestamps and source clock. Align only past quotes within declared freshness. Measure signed decision/arrival execution cost and full shortfall including unfilled opportunity cost and actual fees. Test algebra, sell signs, cancellations, missing/stale quotes and no future benchmark.
- [x] Chronological holdout protocol for prediction error and market-adjusted post-trade response, with minimum group counts and no causal interpretation. Genuine real-order calibration remains pending if no files are supplied. Document file contracts and runnable synthetic verification separately.
- [x] Independent review and local Python/web/static/browser checks.

Delivery follows the repository PR/CI/merge/deploy workflow; final remote validation and cleanup outcomes are recorded in the PR rather than assumed here.

## Review focus

Partial/missing fills cannot disappear; order siblings cannot cross train/test; stale/future quotes cannot become benchmarks; observed price movement cannot be called causal impact; conditional covered-order costs cannot be plotted as unconditional execution costs. Synthetic evidence must stay clearly labeled and never satisfy an actual-calibration gate.

Verified scope: full event reconstruction remains blocked and has not been reconciled; participation is explicitly unavailable pending the volume contract. Only the snapshot counterfactual and research entry are complete. Actual order files were requested but not supplied; the80-parent fixture remains synthetic. No new real trades were placed.
