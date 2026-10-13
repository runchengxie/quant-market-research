# Explicit nontrading valuation events

**Goal:** Separate declared nontrading valuations from executable bars without changing cash, legal holdings or default missing-mark rejection.

**Architecture:** A timezone-aware valuation event establishes a nontrading state and a per-share mark at its effective time. Later valuation events may change that mark but never make the instrument tradable. Apply events before sizing and at their own timeline instants. Retain event provenance, source time and a valuation ledger. Research assembles declared impairment/observed-price policies outside the provider and reruns funded pilots in fresh external directories.

**Authorization:** The user requested implementation exploration after the four-step recommendation: independent valuation events; CNY 1m/10m full impairment pilots; separately qualified quote scenario; disposal only after separate rules. No actual disposal is in this scope.

**Constraints:** No vendor records in provider; preserve defaults, corporate entitlements, quantity, cash and old studies. Reject duplicate/invalid events and conflicting executable bars. Mark source times remain inspectable; no future price backfill. Zero marks cannot cause division by zero for positive targets. Event-based nontrading eligibility cancels affected orders and blocks new trading. A recognized persistent event mark is explicitly an assumption, not an observed daily quote.

- [x] Add synthetic red tests for zero/nonzero valuation, causal event timing, persistent explicit marks, unaffected missing marks, no cash/share mutations, no affected fills, positive target guard, receivables, duplicate/invalid/conflicting inputs.
- [x] Implement event contract, lifecycle, valuation ledger and provenance; keep no-event behavior unchanged.
- [x] Validate full provider suite and lint; independently review, PR and merge provider before pinning consumer.
- [x] Add source-bound research policy assembly, receipt/fingerprint/CLI support and regression tests; default unchanged and scenarios labeled.
- [x] Freshly rerun two capital pilots under explicit full impairment; independently reconstruct all ledgers. Observe-price scenario remains qualified by single-source evidence and gap rules.
- [ ] Record reviewed outcomes/limitations, validate and merge consumer; keep incomplete matrices nonpublic and preserve original 18 results.

Decision: exact legal-date availability remains unknown for one stock, so strict modes reject. Added explicitly declared first-session-after-confirmed-termination modes, retaining this limitation. Source facts and native quotes are hash-bound; quote availability is next-calendar-day09:00 and recognition moves to the actual session calendar. Two alternatives x two capitals complete and independently reconstruct 242 sessions each with zero accounting errors; no event creates cash or removes legal inventory. Each policy remains two of nine, unpublished. Provider PR154 merged63abaf53; installed merged source hashes equal frozen run hashes.
