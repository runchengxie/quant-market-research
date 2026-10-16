# Prospective execution holdout: registration and archive contract

[简体中文](execution-validation-holdout-archive.zh-CN.md)

This is an operational contract for a future replacement cohort. It does not register or start one. Protocol v1 and its recorded hashes remain historical, and the missed 2026-10-15 start must not be reconstructed as unseen evidence. The frozen study design remains in [the v1 protocol](execution-validation-followup-protocol.json); see the [status and data-gap note](execution-validation-next-stage.md) before planning a new version.

## Readiness finding

The repository contains preparation and replay tools for historical execution-validation suites (`prepare_execution_validation_suite.py` and `run_execution_validation_suite.py`). They do not register a prospective cohort or capture daily holdout receipts. The project data directory contains historical validation suites, but no prospective 252-session cohort directory. Do not treat historical suite outputs as prospective records. The following contract defines the missing handoff; daily capture automation must be implemented and rehearsed against synthetic fixtures before the cohort is registered.

## External cohort layout

Keep all cohort records outside Git under the stable project data root:

```text
$DATA_ROOT/quant/quant-market-research/ashare_execution_costs/prospective-holdout/<cohort-id>/
  registration.json
  protocol.json
  session-calendar.json
  sessions/
    YYYY-MM-DD/
      pre_session.json
      post_session.json
      <registered source and ledger artifacts>
      corrections/                 # append-only, only when needed
```

Use a new cohort ID and a new protocol version. Do not edit or copy over v1 in place. Make the registration package immutable before the first eligible exchange session. The package must bind:

- Cohort ID, schema version, UTC registration time and the explicitly determined first session date.
- Exact protocol bytes and SHA-256; duration (252 exchange sessions); primary/secondary comparisons, parameters, metrics, uncertainty method, support rule, interim-visibility boundary and missing-data policy.
- Git commit plus SHA-256 fingerprints for the selection, execution and evaluation code and configuration that will produce the records.
- Source identities, version IDs, coverage definitions and hashes for the exchange calendar, daily/universe inputs, announcements and ST evidence, minute data, fees and corporate-action/valuation inputs.
- The capture schedule and accountable operator, destination path, retention/backup policy, and the recovery procedure for late, incomplete or corrupt files.

The registration record contains the hash of the exact adjacent `protocol.json` and `session-calendar.json` bytes. Each receipt binds the hash of the exact `registration.json` bytes. The calendar file lists its source and 252 session dates; registration binds the per-session decision, open, entry-cutoff and closeout times. An operator must verify the authoritative calendar before registration. Machine-readable contracts are the [registration schema](schemas/execution-validation-holdout-registration.v1.schema.json), [calendar schema](schemas/execution-validation-session-calendar.v1.schema.json) and [session-receipt schema](schemas/execution-validation-holdout-session-receipt.v1.schema.json). The validator checks that the calendar bytes match their fingerprint, its dates match the registered schedule, and the dates/timestamps are well formed and ordered; it does not fetch or independently attest the exchange calendar. A code, source, parameter or missing-data-policy change requires a separately versioned protocol and a new prospective window; it cannot silently alter an active cohort.

## Per-session receipt

For every eligible session, create a `pre_session.json` and a `post_session.json` in `sessions/YYYY-MM-DD/`. This split allows inputs to be receipted before the registered entry cutoff and fills/valuations to be receipted after the session. Both receipts are inventory and completeness records only; they must not contain NAV, returns, drawdown, capacity, fill-rate summaries or other performance results. Each binds the session to the registered cohort and includes:

- `schema_version`, `cohort_id`, `session_date`, `captured_at_utc`, `capture_phase`, and `registration_sha256`.
- `status` (`complete` or `blocked`) and explicit missing/late artifact reasons. An empty event table is not evidence of complete event-source coverage.
- A `pre_session` artifacts map for the full candidate universe, selection targets, input/source manifests, announcement and ST evidence, minute-data manifest and engine/config fingerprints; and a `post_session` artifacts map for the complete cash/holdings/orders/fills/valuation ledgers.
- Stable artifact IDs are `candidate_universe`, `targets`, `input_manifest`, `announcement_st_evidence`, `minute_data_manifest`, `engine_config_fingerprint` and `cash_holdings_orders_fills_valuation_ledgers`. The strict schemas reject other IDs and all unregistered receipt fields, including performance fields.
- For each artifact: a path relative to that session directory, byte size and SHA-256. Do not put private absolute machine paths in the receipt.

Write `pre_session.json` at or after the registered decision time and before the registered entry cutoff. Write `post_session.json` no earlier than the registered closeout time, and after the pre-session receipt. The registration time must precede the first session's decision time. If capture is incomplete, record `blocked`, preserve the missing items and do not backfill that session later as a valid prospective sample. A correction is a new versioned object with its own receipt and a reference to the superseded file; never overwrite bytes already used.

## Safe daily checks and closeout

Run the completeness-only validator after the session's post-session capture:

```bash
uv run python scripts/validate_execution_holdout_archive.py \
  --root "$HOLDOUT_ARCHIVE_ROOT" \
  --through-session-date YYYY-MM-DD
```

Run the temporary synthetic rehearsal separately:

```bash
uv run --locked --extra dev pytest -q tests/test_execution_holdout_archive_validator.py
```

Both arguments are required; the tool has no default data path. It checks registration, protocol and calendar fingerprints, that the calendar's ordered dates match registration, receipt schema/status/timing, artifact-relative paths, file sizes and SHA-256. It hashes artifact bytes without parsing them, including ledgers, and emits only completeness status/errors. It does not verify that an operator's registered exchange calendar is authoritative. Existing historical replay scripts are not suitable for this daily check because running them produces evaluated results. The synthetic command creates a temporary archive in the test runner's temporary directory; it does not create a cohort or touch project DATA_ROOT.

After 252 eligible sessions, freeze the archive and independently verify the registration hash, every daily receipt, artifact hash, sequence and all blocked/corrected sessions. Only then perform the one-time evaluation specified in the registered protocol. If terminal marks or disposal proceeds are unresolved, report final NAV as incomplete and do not publish full-period performance.

## Start checklist

- [ ] A new protocol version is reviewed and its exact bytes are archived without changing v1.
- [ ] Registration contains the fields above and is timestamped before the first eligible session.
- [ ] External DATA_ROOT destination, permissions, immutable retention and backups are verified.
- [ ] Daily capture and completeness-only validation have passed the documented synthetic rehearsal; tests create no real session or DATA_ROOT file.
- [ ] Failure handling prevents late data from being relabeled as timely and corrections from overwriting original inputs.
- [ ] Interim access is restricted to completeness metadata; performance output remains unavailable until one-time closeout.
