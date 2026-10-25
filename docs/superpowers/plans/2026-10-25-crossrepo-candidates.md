# Cross-repository candidate acceptance plan

Goal: Extend the existing synthetic workflow with explicit official-provider SHA candidates and retained machine evidence, without changing committed pins.

Architecture: Keep the current locked zero-skip test gate. A stdlib runner copies consumer sources/manifests into a disposable directory, uses uv dependency overrides there, and invokes the same real synthetic CLI with explicitly validated expected commits. Retain original/resolved locks, command exits, package provenance and receipts in a CI artifact.

Constraints: Official runchengxie repositories only; complete lowercase SHA; no secrets, shared data or production services; no shell interpolation of candidate inputs; no implicit promotion.

Review focus: unknown provider keys, malformed SHA, alternate source URLs, conflicting platform/contracts revisions, missing dependencies and failed command receipts.

- [x] Add and observe failing tests for candidate validation and expected-revision handling.
- [x] Implement the narrow candidate control surface and existing CLI expectation override.
- [x] Extend the existing workflow with optional dispatch JSON, failure receipts and artifact upload; document use.
- [x] Run complete Python suite with all extras, Ruff, real current/candidate chain and diff checks; request independent root diff review before merge.
