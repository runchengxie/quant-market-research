# Implement microcap missing-price repair audit

## Goal

Deliver an evidence-backed microcap missing-price audit, labeled return sensitivities, freshness metadata, and web/documentation updates while keeping the strict NAV as the primary result.

## Architecture

- Reuse the existing pandas/DuckDB reconstruction outputs for strict, partial, and carry-return diagnostics.
- Add a small pure classification module that joins missing holdings to next observed quote, instruments, ST events, and optional suspend_d events.
- Add a report microcap-repair CLI command that writes reproducible CSV/JSON artifacts outside the Git repository by default.
- Publish only a reviewed, explicitly exploratory JSON summary to the web; do not replace the strict microcap NAV with a repaired curve.

## Tech stack

Python, pandas, DuckDB, pytest, Ruff, existing React/Vite web data manifest.

## Spec

See docs/superpowers/specs/2026-09-18-microcap-repair-full-design.md.

## Tasks

1. Implement pure missing-row evidence classification and unit tests.
2. Add the repair-audit CLI, report files, and integration tests.
3. Fetch/use the available TuShare suspend_d asset and run the full 2008–latest audit; preserve unresolved gaps.
4. Update microcap research docs and web freshness/quality metadata with the reviewed summary.
5. Run the full test/lint suite and targeted real-data smoke test.
6. Commit, create/merge the GitHub PR, and remove the feature branch/worktree after verification.

## Verification

- pytest -q
- ruff check src tests
- CLI report on the configured latest A-share data root.
- Assert strict primary output is unchanged and web JSON labels all repair outputs as exploratory.
