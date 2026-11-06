---
role: reviewer
status: escalate
verdict: GO
reasons: [gauntlet green, no blocking finding, 2 major findings open (atomicity unproven, unknown-slot exception), escalate because the diff adds the storage adapter named in Sensitive zones]
severity: major
open_majors:
  - "Atomicity of check-and-save is built but proven by no test: removing the lock from atomically passes every test and every PIT mutant (simultaneous booking outcome stays an open product question)."
  - "BookSlot.book on an unknown slot id throws NoSuchElementException (orElseThrow), a caller-visible behavior no document settled for story 1; story 2 criterion 1 / D-26 replace it with Refused(UNKNOWN_SLOT). Story 1 must not be released alone."
---

# Pre-merge review, claude-bank-account-poc-1435f8 (medical-appointments, story 1), iteration n=1

**Verdict: GO** (escalate: sensitive zone touched)
**Date**: 2026-10-18 · **Base**: f67bd8c..HEAD (8baeef1) · **Scope**: 19 files, +387 lines, 5 commits, folder examples/medical-appointments only
**Criticality**: critical. Signals: domain layer, test-cases `priority: high`, an invariant on the persisted-state port.

Skill announced: `premerge-review`.

## Summary

Story 1 is implemented as planned: typed outcome (D-25/D-26), single rule class (D-21), derived "free" state, atomic unit through the port, hexagonal layers respected. The gauntlet is green and my own broken-rule checks are caught, except the lock. Two major findings stay open; neither reaches the three-major threshold, so GO. Escalation is set because `InMemoryBookingStore` is a storage adapter for bookings (Sensitive zones): the human should know it exists. Content is ids only, in memory, no logging, no exposure, so I found nothing to block.

## Gauntlet

| Check | Result |
|---|---|
| Test suite | OK (7 tests incl. ArchUnit; also run in scratch copy as baseline) |
| Lint / format | not available (no linter configured, D-18 skipped Checkstyle) |
| Harness invariants | INV-001 exit 0; INV-002 7 covered_ok, 0 broken, 0 orphan |
| Test-case bridge | OK |
| Mutation (critical) | INV-003 score 100.0% (7 killed / 7 generated), no threshold set (warn) |
| Test-cases touched | 7 read, all in docs/business/test-cases/book-a-slot/ |

Command: `bash tools/harness/run_all.sh --with-mutation`, harness exit 0.

## My own broken-rule check (scratch copy outside the repository, tests only: mvn -o test)

| Mutation | Result |
|---|---|
| taken check removed | caught (3 tests) |
| own-held slot allowed | caught (2) |
| wrong refusal reason | caught (3) |
| booking saved on refusal | caught (1, sequence test only) |
| all slots share one booking key | caught (2) |
| booking carries wrong patient | caught (4) |
| booking carries a fixed slot | caught (2) |
| lock removed from `atomically` | **survives** (no concurrent test) |

The tests protect the behaviors of the criteria. Note that the "booking saved on refusal" mutant is caught by the sequence test alone: it carries real weight.

## Test-cases (angle 3, what before how)

The 7 test-cases state what the stories say (criteria 1-6, req 1-5, 11, 12), in business words, no class names. Vocabulary matches the PRD (booking, slot, taken, patient). No drift. No glossary exists yet (stories.md says so), so none to check.

## Findings

### Blocking
None.

### Major
- **[M1] Atomicity of check-and-save is unproven** — `src/main/java/io/example/medical/adapters/InMemoryBookingStore.java:50` (`atomically`), `application/BookSlot.java:19` · angle: bugs
  Req 5 and architect.md rely on the lock so that two simultaneous bookings cannot both succeed. Removing the lock leaves all 7 tests green and PIT at 100% (verified). Known and declared in plan section 6 and the developer note. Consequence: a regression of the one mechanism guarding "no double-booking" under concurrency is invisible to the harness. Recommendation: carry to the request that settles the simultaneous outcome; there add a concurrent test (two threads, one slot, exactly one `Booked`). Not blocking: the test boundary and open question are documented.
- **[M2] Unknown slot id: `NoSuchElementException`** — `application/BookSlot.java:20` · angle: bugs
  Position on the developer's "Behaviors added": this is a caller-visible behavior (an unchecked exception leaks through `BookSlot.book`, not a typed outcome) that D-25 contradicts in spirit (a refusal is a typed result) and that no document settles for story 1. Story 2 criterion 1 and D-26 `UNKNOWN_SLOT` settle the end state, and the plan says it is unspecified and untested until then. Rule applied: unsettled consumer-visible behavior is major, not minor; it goes to `open_majors` so story 2's planner closes it. Rated major, not blocking, because the exception message ("No value present") exposes nothing and the plan forbids releasing story 1 alone. Recommendation: do not release before story 2 lands; the story 2 plan replaces `orElseThrow()` by `Refused(UNKNOWN_SLOT)` and tests it.

### Minor
- **[m1] `null` identifiers** — `domain/*Id.java` · angle: bugs. Position: covered, not a finding of its own. D-22 defers empty, blank and absent identifiers explicitly, so the behavior is settled as "unspecified". Observed consequence worth the next planner's knowledge: `book(null, S)` on a free slot returns `Booked(Booking(null, S))` and stores it, whereas an absent slot id throws M2. No action in this request.
- **[m2] `slotIsNoLongerFreeAfterBooking` asserts only `isPresent()`** — `BookSlotTest.java:45` · angle: debt. Other tests pin the exact booking; fine, but the test-case wording "no longer free" is weakly checked on its own. No risk, optional.
- **[m3] `findSlot` reads without the lock** — `InMemoryBookingStore.java:28` · angle: debt. Safe today (map filled in the constructor, never changed, final field); a comment would protect it if slots ever become mutable (F4.1 preload). Developer noted it.
- **[m4] Mutation run via `--scope critical` instead of `diff`** — harness; same result on a greenfield. Baseline for INV-003 is not recorded in invariants.md (100.0%, 7 mutants); to record by the next owner of that file.

## Sensitive zones

The diff adds `InMemoryBookingStore`, a storage adapter for bookings. It stays in memory, holds ids only (no name, no health data), is not exposed, and logs nothing; no error message carries personal data. Layer rule (INV-001) respected: domain imports only the JDK, application imports domain, no inner layer imports adapters. `escalate` is therefore for acknowledgment, not for a defect: any future persistence or exposure must return to the human.

## Checks not performed

- Concurrency behavior: not testable with the sequential boundary of the plan (see M1).
- No linter exists; no glossary exists; no CI file (D-17).

## Positive notes

- TDD discipline shows in the history, and the developer states honestly which tests passed first time.
- The rule is one class, one place, ready for D-21 order; "free" is derived, so req 5/12 hold by construction.
- Developer note lists its added behaviors openly, including the exception.
