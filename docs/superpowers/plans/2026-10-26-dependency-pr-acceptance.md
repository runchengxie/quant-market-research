# Dependency PR acceptance

Goal: Automatically validate the checked-out consumer against the exact official provider combination declared by its manifest and committed lock. Formal upgrade PRs must synchronize the public default pin declarations; tests must cover both default entrypoints and the selected locked combination.

Design: A stdlib-only selection step validates five locked Git sources (official repository, full SHA, exact contracts subdirectory), coordinated platform/contracts, and all explicit manifest/override references before installation. The existing read-only pull_request workflow uses the selected mapping for synthetic tests/CLI and the disposable acceptance runner. Automatic locked mode copies the lock without re-resolution; manual candidates retain explicit isolated override resolution. No PR text, labels, privileged triggers, secrets or writes to source pins.

- [x] Reproduce upgraded-lock selection, source/manifest disagreement and untrusted/ambiguous sources with failing tests.
- [x] Add strict locked selection, route existing tests/CLI/runner through it, and retain no-relock receipt evidence.
- [x] Run normal/no-formal control tests, complete all-extras suite, current and changed-pin disposable acceptance, Ruff/diff and exact-head CI.
- [ ] Independent root review, merge only after target/head checks, and task-only cleanup.

Review correction: the first implementation switched all chain tests to explicit expected maps, leaving the public default entrypoints uncovered after a manifest/lock-only bump. Root review rejected that coverage gap. The final design retains literal default pin declarations, verifies them against formal locks before installation, and keeps actual default API and CLI acceptance tests. Explicit temporary candidates remain separate.
