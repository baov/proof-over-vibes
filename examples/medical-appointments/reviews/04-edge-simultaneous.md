---
role: reviewer
status: done
verdict: GO
reasons: []
severity: minor
open_majors: []
---

# Pre-merge review: edge-simultaneous (iteration 1)

**Verdict: GO**
**Date**: 2026-10-18 · **Base**: f71b308..HEAD (ffffc73) · **Scope**: `examples/medical-appointments` only, 13 files, +574/-108 (test code, 9 test-case files, one Javadoc sentence on `BookingStore.atomically`)
**Criticality**: low (tests plus one comment), read in full anyway; no sensitive zone touched (no storage or exposure of booking data), so no `escalate`.

## Summary

The code already met the PRD; the diff is proof. The nine concurrency tests replace a timed 500 ms wait with a condition gate (`Race`) and assert the loser's reason. Removing the lock fails 7 of 9 tests on every run (24 mutant runs, 0 survivor); the real code passes 50 of 50 runs. Remaining findings are minor.

## Gauntlet

| Check | Result |
|-------|--------|
| Test suite (`mvn -o test`) | OK (35 tests) |
| Lint / glossary | OK (`check-glossary.sh`: repository is English) |
| Harness invariants | INV-001 OK; INV-002 35 covered_ok, 0 broken, 0 orphan |
| Mutation (diff) | PIT 100 % (29/29), no threshold set (human decision, unchanged); nothing in `domain`/`application` changed |
| Test-cases touched | 9 read (new or rewritten under `docs/business/test-cases/book-a-slot/`) |

`run_all.sh --with-mutation` exit 0.

## Do the tests pass without the lock? (scratch copy outside the repository)

Mutants applied to a copy in the scratchpad; the repository was not touched. Each mutant run 8 times (separate Maven runs) on `BookSlotConcurrencyTest`.

| Mutant | Result |
|---|---|
| `atomically` body = `unit.get()` | 8/8 runs fail, 7 tests each time (1 to 6 and 9); 7 and 8 stay green as planned |
| plus unlocked `save` | 8/8 runs fail, same 7 tests |
| Clock read before the unit | 8/8 runs fail, test 6 only (better than the "accepted limit" the plan names: the hoisted read before the unit is caught) |
| Check inside the unit, `save` after it | 3 of 8 runs PASS; the 5 failures come mostly from test 6 (see m1) |
| Check outside the lock (only `save` in `atomically`) | 8/8 fail, but with "the race never formed" after the 10 s guard, not with a double booking (see m2) |
| One lock per slot, `atomically` unused | fails the same loud way (gate never forms, N x 10 s); I stopped the run before it finished (see m2) |

Flakiness on the real code: 25 runs idle plus 25 runs with 2 busy loops per core, 50/50 green, no "race never formed". Each class run takes well under a second.

Gate review: sound. A racer counts as held back only if it has `entered` the store and is arrived, finished or parked in a frame whose first non-JDK method is `atomically`; `racers` is published before start; a racer that dies counts as finished; requests that skip the store (missing identifier) simply finish. Failure modes are loud: `IllegalStateException` after 10 s, `AssertionError` after a 20 s join. No test asserts nothing (the discarded `winnerOf` calls assert inside). No test hard-codes a winner against D-35: test 5(c) and the unknown-slot and missing-identifier tests name a winner only because every other request is forced to lose (C holds an overlapping slot, the others are invalid).

## Planner's flag (third party's reason depends on arrival order): not major

Case: C holds X overlapping S; B and C race for S. B is `Booked` either way; C sees `TAKEN` if B is judged first, `OVERLAPPING` if C is. This is a behavior a consumer sees, so the rule applies; but a document settles it. D-21 fixes the order of refusals (taken before overlap), D-35 says no one may rely on who is judged first, and the PRD's measure (section 2) says the outcome is one some sequential order gives. C gets exactly what it would get calling after B or before B. Test 5(c) pins both outcomes through the oracle. It is therefore decided, not open: no `open_majors`. A product owner who wants `TAKEN` in every order would be asking a new rule that changes D-21, which is a separate request.

## Findings

### Blocking
None.

### Major
None.

### Minor
- **[m1] "Save outside the lock" is caught only by luck** — `Race.java:96-110` (gate in `slotsHeldBy`) · angle: bugs. The gate forces the interleaving between the reads and the decision, not the window between the unit's end and the `save`. With `save` moved after `atomically`, 3 of 8 runs passed; the other 5 failed mostly through test 6 (the clock flips in `save`). Considered `major` (a plausible concurrency bug survives a run), kept `minor` because removing the lock, the stated target, is caught every time. Recommendation: let the gate also hold a racer right after `decide` and before `save` (a second wait inside `GatedStore.save`, same rule), so that this bug gives a double booking on every run.
- **[m2] A misplaced lock is detected through the gate's coupling to `atomically`, and the guard compounds** — `Race.java:96-110` · angle: bugs/debt. Check-outside-the-lock and per-slot-lock variants fail with "the race never formed" (`entered=0`), not with a double booking. Each racer that times out frees the lock for the next, so one race can last about N x 10 s (50 s for the five-patient test); the 20 s join then ends it, leaving non-daemon threads to run out their own guard. Bounded, never infinite, and only in a broken build. Recommendation: let the first guard that fires make the other racers of that race stop at once (shared "aborted" flag checked in the spin loop), and say in the Javadoc that the gate assumes the store calls `atomically`.
- **[m3] Class Javadoc says "no test names the winner"** — `BookSlotConcurrencyTest.java:35-38` and `:158` · angle: debt. Test 5(c) asserts `Booked(B, S)`; it is deterministic (C is always refused by its own held slot), but the Javadoc is then slightly untrue. Recommendation: one clause saying a winner is named only where every other request is forced to lose.
- **[m4] The test 5 oracle is `BookSlot` run in sequence** — proves concurrent equals sequential, not that the sequential rule is right (the developer and plan say so; `BookSlotTest` carries the rule). Recorded, no action.

## Checks not performed

- Lock removal for a real shared database adapter: out of scope (per process only, recorded by the new Javadoc sentence).
- Mutation baseline: still a human decision (carried minor).

## Positive notes

- The 500 ms timed wait is gone; the oracle (some sequential order, computed not hard-coded) fits D-35 and the PRD's measure.
- The developer found the gate flaw (a thread blocked on class loading) through its own lock-removal proof and fixed it; my 24 mutant runs reproduce its claim (7 of 9 fail every run).
- Test-cases are in business words, one per test, INV-002 green; the production change is one honest sentence.
