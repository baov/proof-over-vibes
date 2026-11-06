---
role: reviewer
status: escalate
verdict: GO
reasons: [gauntlet green, no blocking finding, no major finding, the carried-over majors M1 and M2 are closed, escalate because the diff modifies the bookings storage adapter named in Sensitive zones]
severity: minor
open_majors: []
---

# Pre-merge review, claude-bank-account-poc-1435f8 (medical-appointments, story 2: refuse-unhonourable), iteration n=1

**Verdict: GO** (escalate: sensitive zone touched)
**Date**: 2026-10-18 · **Base**: 2313fa2..HEAD (b900bcb) · **Scope**: 24 files, +696/-14 lines, 7 commits, folder examples/medical-appointments only
**Criticality**: critical. Signals: domain layer (`BookingRule`, `TimeRange`, `Slot`), test-cases `priority: high`, a change of public signatures (`Slot`, `BookSlot`, `BookingStore`, `BookingRule.decide`).

Skill announced: `premerge-review`.

## Summary

Story 2 is implemented as planned and decided: unknown slot, past, taken, overlap, in the single order of D-21, all in `BookingRule`; `TimeRange` valid by construction (D-27, D-29); overlap per patient (D-28). The two majors carried over from story 1 are closed: M2 by `Refused(UNKNOWN_SLOT)`, M1 by two concurrency tests that I saw fail without the lock. I found no blocking or major finding, only minor ones. The zone check escalates the review, as in story 1, because `InMemoryBookingStore` (bookings storage) is modified; it still holds ids only, in memory, with no log and no exposure.

## Gauntlet

| Check | Result |
|---|---|
| Test suite | OK (22 tests including ArchUnit and the 2 concurrency tests) |
| Lint / format | not available (no linter configured, D-18) |
| Harness invariants | INV-001 exit 0; INV-002: 22 test-cases, 22 covered_ok, 0 broken, 0 orphan |
| Test-case bridge | OK (part of INV-002) |
| Mutation (critical) | INV-003: 100.0% (18 killed / 18 generated), no threshold set (warn) |
| Test-cases touched | 15 read (all new, in docs/business/test-cases/book-a-slot/); 7 of story 1 unchanged |

Command: `bash tools/harness/run_all.sh --with-mutation` from the project folder, harness exit 0.

## My own checks (scratch copy outside the repository, `mvn -o test`)

**Concurrency tests really need the lock (M1).** `atomically` reduced to `unit.get()`: both `BookSlotConcurrencyTest` tests fail ("both bookings of the same slot succeeded", "a patient booked two overlapping slots"); with the lock they pass. Reproduced; the claim of the developer holds. The tests inspect neither the type nor the reason of the other attempt.

**Refusal order, all 24 permutations of the four checks in `BookingRule`.** Every permutation that puts past, taken and overlap in a different relative order than P < T < O is killed. The only survivors are the permutations that move "unknown" among the others, which is behavior-equivalent (an absent slot cannot also be past, taken or overlapping once guarded). So each pair of D-21 is pinned: past/taken, past/overlap, taken/overlap (the own-held slot included), unknown/anything.

**Edges, mutated one at a time, all killed:** past `<` turned into `<=` and into "1 ns earlier"; overlap `start <= otherEnd`; overlap `otherStart <= end`; overlap one-sided; range accepting a zero length; range not rejecting a null end; clock ignored; held slots ignored; held slots of any patient instead of the booking patient. Exactly now: booked; 1 ns before: PAST; 1 ns after: booked. Back to back both sides: booked; 1 ns of overlap at either end: OVERLAPPING; zero-length slot: cannot exist (`IllegalArgumentException`); 1 ns long: valid.

**Probe of unspecified inputs** (not committed): null patient is stored; a null slot id or an empty id throws `NullPointerException`; a null clock throws. See m1.

## Test-cases (angle 3, the what before the how)

The 15 new test-cases say what story 2 and its decisions say (criteria 1-12, D-19, D-20, D-21, D-26, D-27, D-28), in business words, no class names, vocabulary of the PRD (booking, slot, taken, patient). The two simultaneity test-cases honestly say that what the other person is shown is not specified, and cite "PRD req 5 only". No test-case describes a wrong behavior. No project glossary exists (stories.md says so), nothing to compare vocabulary against.

## Carried-over majors

- **M1 (atomicity unproven): closed.** Two tests, deterministic through the bounded-wait decorator, fail without the lock; the loser's outcome is not decided by them.
- **M2 (unknown slot throws): closed.** `Refused(UNKNOWN_SLOT)`, test `refusesAnUnknownSlot`, no `orElseThrow` left in `src`.
- Minors of story 1: `findSlot` now carries a comment; `slotIsNoLongerFreeAfterBooking` asserts the exact booking; `null` identifiers still deferred (D-22); no mutation baseline (human decision).

## Sensitive zones

Escalate. The diff modifies `InMemoryBookingStore` (storage adapter for bookings: a person linked to a practitioner, GDPR Article 9 context, unverified) and adds a new read, `slotsHeldBy(patient)`, which lists what a patient holds. It is internal to the use case, returns slots (practitioner id and time range), and nothing is logged or exposed. `TimeRange`'s exception message carries instants only, no identifier. No persistence, no dependency, no `pom.xml` change. I found nothing to block; a person should acknowledge that the zone was touched.

## Findings

### Blocking
None.

### Major
None.

### Minor
- **[m1] A stored booking with a `null` patient makes every later booking by anyone throw** — `InMemoryBookingStore.java` (`slotsHeldBy`, `booking.patient().equals(patient)`) · angle: bugs. Probe: `book(null, slot)` returns `Booked`; the next `book(anyone, anySlot)` throws `NullPointerException`, because every attempt scans all bookings. In story 1 the same input was stored harmlessly; the new scan widens its effect from one slot to the whole store. D-22 defers identifiers and says "unspecified", so I did not raise it to major (the question is already recorded as open, the planner already knows it). Recommendation: when D-22 is taken up, decide it with this effect in mind; meanwhile `patient.equals(booking.patient())` would at least not poison other patients (it is not a decision on D-22 itself).
- **[m2] Who loses a simultaneous booking is now decided in fact, and written nowhere** — `BookSlot.book` · angle: compliance. Because the rules run inside the atomic unit, the loser gets `Refused(TAKEN)` (same slot) or `Refused(OVERLAPPING)` (same patient). The PRD section 6, the test-cases and the plan all keep it open on purpose, and the tests do not pin it, so a later request can still choose. Recommendation: keep the question open until the edge-case request; that request should confirm or change what the code already does.
- **[m3] The concurrency tests can pass without the lock on a very slow machine** — `BookSlotConcurrencyTest.java` (`MAX_WAIT_MILLIS = 500`) · angle: bugs (test strength). The decorator makes the bad interleaving certain only if the second thread reaches `slotsHeldBy` within 500 ms of the first; a heavily loaded CI could let the wait expire and the test pass without the lock (a false pass, never a false failure). Reproduced as failing without the lock on this machine. Recommendation: raise the wait or note the assumption in the test comment; low priority.
- **[m4] `reportsUnknownBeforeAnyOtherRefusal` pins little** — `BookSlotTest.java` · angle: debt. An absent slot has no other property, so the pair "unknown with another rule" cannot occur; the test still guards against an exception on a patient who holds slots, which is useful. All 24 order permutations showed the equivalent ones survive. Recommendation: say in the test-case that "unknown first" is structural.
- **[m5] Duplicate slot ids in the preload silently keep the last slot** — `InMemoryBookingStore` constructor · angle: bugs. Preload design is out of scope (F4.1); a duplicate id loses a slot with no error. Recommendation: raise it when the preload is designed.
- **[m6] Stale statement in `docs/technical/invariants.md`** — INV-003 "Baseline: not measured (no production code yet)"; production code now exists and the run gives 18/18. The decision to record a baseline and a threshold belongs to a person; the sentence is simply outdated. Same for `.metrics` (story 2 metrics are the Orchestrator's, not yet written).

## Checks not performed

Lint: none configured. No project glossary to check vocabulary. Persistence, exposure and authentication do not exist yet, so security was checked only on identifiers, exception messages and logging (none). Each of the 7 commits was not rebuilt separately; I reviewed the final state and the sequence from the developer's note.

## Contradictions with the PRD and the decision log

None found. PRD req 10 ("longer than zero") agrees with D-27 (zero-length rejected); req 7 and 10 agree with D-19, D-20; PRD section 6 still lists the simultaneous outcome and blank identifiers as open, which the code leaves open (m1, m2). D-26's note "story 1 produces only TAKEN" is history (append-only log) and no longer true, which is expected.

## Positive notes

- The order of refusals lives in one method and is pinned pair by pair; I could not move a real pair without a test failing.
- The concurrency proof is deterministic by construction and cleanly avoids deciding the product question.
- The slice stays inside the plan: no behavior added beyond the stories, the decisions and their open points.
