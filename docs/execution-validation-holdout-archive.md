# Prospective execution holdout: registration and archive contract

[简体中文](execution-validation-holdout-archive.zh-CN.md)

This is an operational contract for a future replacement cohort. It does not register or start one. Protocol v1 and its recorded hashes remain historical, and the missed 2026-10-15 start must not be reconstructed as unseen evidence. The frozen study design remains in [the v1 protocol](execution-validation-followup-protocol.json); see the [status and data-gap note](execution-validation-next-stage.md) before planning a new version.

## Readiness finding

The repository contains preparation and replay tools for historical execution-validation suites (`prepare_execution_validation_suite.py` and `run_execution_validation_suite.py`). They do not register a prospective cohort or capture daily holdout receipts. The project data directory contains historical validation suites, but no prospective 252-session cohort directory. Do not treat historical suite outputs as prospective records. The following contract defines the missing handoff; daily capture automation must be implemented and rehearsed against synthetic fixtures before the cohort is registered.

## External cohort layout

Keep all cohort records outside Git under the stable project data root:

```text
$DATA_ROOT/quant/quant-market-research/ashare_execution_costs/prospective-holdout/<cohort-id>/
  registration/
    protocol.json
    registration.json
  sessions/
    YYYY-MM-DD/
      receipt.json
      <registered source and ledger artifacts>
      corrections/                 # append-only, only when needed
```

Use a new cohort ID and a new protocol version. Do not edit or copy over v1 in place. Make the registration package immutable before the first eligible exchange session. The package must bind:

- Cohort ID, schema version, UTC registration time and the explicitly determined first session date.
- Exact protocol bytes and SHA-256; duration (252 exchange sessions); primary/secondary comparisons, parameters, metrics, uncertainty method, support rule, interim-visibility boundary and missing-data policy.
- Git commit plus SHA-256 fingerprints for the selection, execution and evaluation code and configuration that will produce the records.
- Source identities, version IDs, coverage definitions and hashes for the exchange calendar, daily/universe inputs, announcements and ST evidence, minute data, fees and corporate-action/valuation inputs.
- The capture schedule and accountable operator, destination path, retention/backup policy, and the recovery procedure for late, incomplete or corrupt files.

The protocol, registration record and every referenced manifest must be hashed as files, not reconstructed from their parsed values. Freeze the cohort before the first eligible session and confirm its registration timestamp precedes that session in Shanghai time. A code, source, parameter or missing-data-policy change requires a separately versioned protocol and a new prospective window; it cannot silently alter an active cohort.

## Per-session receipt

For every eligible session, create one `sessions/YYYY-MM-DD/receipt.json`. The receipt is an inventory and completeness record only; it must not contain NAV, returns, drawdown, capacity, fill-rate summaries or other performance results. It must bind the session to the registered cohort and include:

- `schema_version`, `cohort_id`, `session_date`, `captured_at_utc`, capture phase, and `registration_sha256`.
- Decision and intended-entry timestamps, with time zone, to show that each input was available at the frozen decision point.
- `status` (`complete` or `blocked`) and explicit missing/late artifact reasons. An empty event table is not evidence of complete event-source coverage.
- An `artifacts` map for the protocol's daily archive items: full candidate universe, selected targets, input/source manifests, announcement and ST evidence with availability times, minute-data manifest, engine/config fingerprints, and complete cash/holdings/orders/fills/valuation ledgers.
- For each artifact: a path relative to that session directory, byte size and SHA-256. Do not put private absolute machine paths in the receipt.

Write and verify the receipt before the session's first eligible order/entry. If capture is incomplete, record `blocked`, preserve the missing items and do not backfill that session later as a valid prospective sample. A correction is a new versioned object with its own receipt and a reference to the superseded file; never overwrite bytes already used.

## Safe daily checks and closeout

Daily operational checks may inspect registration status, expected session date, receipt metadata, artifact presence, byte sizes and hashes, timestamps and sequence gaps. They must not parse ledgers, calculate cumulative measures or expose performance outcomes. The current historical replay scripts are not suitable for this daily check because running them produces evaluated results. Until a dedicated completeness-only validator and capture rehearsal exist, the cohort is not ready to start.

After 252 eligible sessions, freeze the archive and independently verify the registration hash, every daily receipt, artifact hash, sequence and all blocked/corrected sessions. Only then perform the one-time evaluation specified in the registered protocol. If terminal marks or disposal proceeds are unresolved, report final NAV as incomplete and do not publish full-period performance.

## Start checklist

- [ ] A new protocol version is reviewed and its exact bytes are archived without changing v1.
- [ ] Registration contains the fields above and is timestamped before the first eligible session.
- [ ] External DATA_ROOT destination, permissions, immutable retention and backups are verified.
- [ ] Daily capture and completeness-only validation have passed a rehearsal using synthetic data; no real session is created by the rehearsal.
- [ ] Failure handling prevents late data from being relabeled as timely and corrections from overwriting original inputs.
- [ ] Interim access is restricted to completeness metadata; performance output remains unavailable until one-time closeout.
