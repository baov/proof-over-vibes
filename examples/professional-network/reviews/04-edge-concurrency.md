---
role: reviewer
status: escalate
verdict: GO
reasons:
  - "Gauntlet green (86 tests, typecheck, harness 0 violation / 85 test-cases covered, selftest 6/6, mutation 100.0% 161/161). Requirements 1 to 6 are covered; the queue is correct and isolates failures."
  - "Escalate: the diff touches src/connections/index.ts and src/connections/infrastructure/, Sensitive zones; a human reviews before merge."
  - "One major left open: a consumer-visible behavior no document settled (an operation that never settles blocks the whole module). Fewer than three majors: GO."
severity: major
open_majors:
  - "An operation that never settles (a store or id generator that hangs) blocks every later operation of the module forever, with no timeout; no PRD, decision or ADR says so (the plan only lists it as out of scope). To be asked by the next planner."
---

# Pre-merge review — claude-bank-account-poc-1435f8 (edge-concurrency, iteration 1)

**Verdict: GO** (status `escalate`: Sensitive zones touched)
**Date**: 2026-10-18 · **Base**: b5938ae..ecfa4ac (HEAD) · **Scope**: 16 files in `examples/professional-network`, +599/-7 lines (12 test-case files, queue 15 lines, `index.ts` 7 wrappers, `concurrency.test.ts` 355, `support.ts` +52). The harness commit 3f0a34b (INV-011) is outside the diff.
**Criticality**: critical — the diff touches `src/connections/index.ts` (public entry point) and `infrastructure/`, both Sensitive zones, and the 12 new test-cases are `priority: high`.

## Summary

The change wraps the seven public operations of `createConnections` in one FIFO promise-chain queue; use cases, store port and public contract are unchanged. The queue is correct: a rejection reaches its own caller and does not block the next operation. The tests would fail if the queue misbehaved, for the writes (see experiment). Residual gaps are one open consumer-visible behavior (hang) and a few documentation drifts. Verdict GO; escalate for human review of the Sensitive zones.

## Gauntlet

| Check | Result |
|-------|----------|
| Test suite (`npm test`) | OK — 10 files, 86 tests |
| Typecheck | OK |
| Harness invariants (`npm run harness`) | OK — layers 0, shape 0, INV-011 (`check_serialized`) 0 violation (now active) |
| Test-case bridge | OK — 85 test-cases, 85 covered_ok, 0 orphan |
| Harness self-test | OK — 6/6 |
| Mutation (`npm run mutation`, critical scope) | 161/161 = 100.0%, threshold none (human, INV-010). The queue is outside the scope (INV-010), so it is not scored |
| Test-cases touched | 12 read (all `concurrency-*.md`) |

### Own experiment on the queue (scratch copy outside the repository; the repository was not touched)

| Mutant | Result |
|---|---|
| Queue is `o => o()` (no serialization) | 8+ tests red (all write races) — caught |
| Tail poisoned by a rejection (`tail = outcome`) | K10 red — caught |
| Caller's rejection swallowed | K10 red — caught |
| Operation starts without waiting for the previous one | Races red — caught |
| `eraseMember` wrapper removed | Erase test red — caught (thanks to the added 0..8-turn loop) |
| `getPairState` and `listPendingRequests` wrappers removed | **86/86 green — not caught** by any test (see m1) |
| One module-level queue shared by all instances | **86/86 green — not caught**; not observable, benign (stricter serialization) |

## Angle readings

- **Failure does not block**: `tail = outcome.catch(() => undefined)` keeps the rejection for the caller (`return outcome`) and clears it for the chain. No unhandled rejection. A synchronous throw inside `operation` becomes a rejection through `.then`. Correct.
- **Nothing reaches the store outside the queue**: the store is created inside `createConnections` and held only by `deps`, captured by the seven wrappers; the public interface has no other path. No module outside `src/connections` imports `application/` or `infrastructure/` (grep: none). Deep imports from outside stay forbidden by INV-004 (warn).
- **"Single instance" assumption of ADR-0002**: enforced by construction for the part that can be: `createConnections` creates its own `InMemoryStore` and takes no store, so two instances can never share a store through the public API (a second instance is independent, not a bypass). Multi-process cannot happen with an in-memory store. The statement "one process only" is therefore only stated, but nothing in the code can currently violate it; the day a persistent store is injected, the ADR and the invariant must change together (ADR-0002 already says new ADR first). No finding.
- **Re-entrancy**: an operation calling another queued operation would deadlock; no code does (use cases receive `deps`, not the wrapped object). Fine.
- **Security / data**: no new input, no dependency, no secret; erase goes through the queue, so no half-erased member is observable.

## Findings

### Blocking
None.

### Major
- **[M1] An operation that never settles blocks the whole module** — `src/connections/infrastructure/serial-queue.ts:10-13` · angle: bugs
  The chain waits for every earlier operation to settle. A store or id generator that hangs (a persistent store later) freezes every call of the instance, reads included, with no timeout and no error. A consumer sees every call hang forever. The plan lists it only as "not tested, out of scope"; neither the PRD, a decision nor ADR-0002 settles it, so per the rule it is a major finding. Recommendation: the next planner asks whether a stuck operation should time out, and states the limit in ADR-0002 (Consequences) in the meantime. No code change is requested here.

### Minor
- **[m1] The two read wrappers are guarded only by a `warn` structural invariant** — `src/connections/index.ts:46-47` · angle: bugs/debt
  K6 is green without the queue by nature (confirmed: removing both wrappers leaves 86/86 green); the Planner accepted it (plan section 8). INV-011 is severity `warn`, so a removed wrapper would not fail the gauntlet. Residual risk accepted by the plan; consider raising INV-011 to `error` now that it is active, or testing reads with a store that opens a real gap when a store other than the in-memory one exists.
- **[m2] `docs/technical/invariants.md` is stale on INV-011** — lines 19 and 149 · angle: debt
  It still says "pending until the queue file exists / is not built yet", while the file exists and the check is active. The Remediation and Fix snippets write `queue.run(() => ...)` whereas the code and the check use `queue(() => ...)`. A doc that lies. Recommendation: set the status to active and fix the snippets.
- **[m3] ADR-0002 contradicts D-37 on arrival order** — `docs/technical/adr/0002-operations-serialized-in-process.md` (Consequences) · angle: compliance
  The ADR says "the order of arrival" decides the winner; D-37 says the module promises no arrival order. The code is FIFO, tests do not rely on it. Recommendation: align the ADR sentence with D-37 ("FIFO today, not a promise").
- **[m4] D-38 "the failed operation wrote nothing" is only proved for an id generator failure** — `tests/connections/concurrency.test.ts` (K10) · angle: bugs
  A failure between the two writes of `saveAccepted` (a future store) would leave an accepted request without connection, then visible to the next queued read. Unobservable with the in-memory store; the queue does not roll back. Recommendation: note it as a precondition for the first non-memory store.
- **[m5] K10 asserts the generator's error by identity, but the D-38 test-case promises it for "something underneath fails" in general** — `docs/business/test-cases/connections/concurrency-failure-does-not-block.md` · angle: debt. Wording only; cover a store failure when one can fail.

## Checks not performed

- Full-diff behavior of a non-memory store (none exists).
- Lint/format: the project has no linter script besides typecheck.
- Root validators (`validate-skills.py`, `check-glossary.sh`) are outside this folder; the developer reports them clean.

## Positive notes

- The oracle (`bothOrders`) checks each concurrent result against the exact outcome of both sequential orders, and every test also asserts its named outcome, so it cannot hide a wrong sequential result.
- The deviation on K6 was stopped on and not faked; the extra 0..8-turn erase loop made the `eraseMember` wrapper observable.
- The queue is 15 lines, dependency-free, one instance per `createConnections`, and the business test-cases are one per behavior with their decision as source.
