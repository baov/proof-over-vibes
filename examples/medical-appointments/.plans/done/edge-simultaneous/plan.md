---
role: planner
status: done
reasons: []
---

# Plan: what the loser of a simultaneous booking sees

Skill announced: `plan-driven-dev` (context and plan steps only). Every situation the PRD lists is decided by a document; no question remains. One consequence (the third-party loser, below) is flagged for the human to read, not asked.

## Decisions applied

- Architect (`structure: unchanged`): decide-then-save already runs inside `atomically`, so the loser is judged by `BookingRule.decide` (D-21, extended by D-34) against the state the winner left. No production code is missing; the gap is proof. The plan stays inside that: it adds no public operation, parameter or type.
- D-31 / PRD req 2: the same-slot loser sees `TAKEN`. D-32 / PRD req 4: the one-patient overlapping loser sees `OVERLAPPING`. D-35 / PRD req 6: either request may win; no test may assume who wins. PRD req 7: the refusal changes nothing; the winner's booking is unchanged. PRD req 5: the reason is the one D-21 gives after the winner's booking.
- PRD section 2 (measure): whatever the timing, the outcome is one that could have happened with the requests one after the other. This is the oracle of the tests.

## What each simultaneous situation shows the loser

| Situation | Loser sees | Decided by |
|---|---|---|
| Two patients, same free slot (case A) | `Refused(TAKEN)`; slot holds the winner only; loser's patient holds nothing | D-31, PRD req 1, 2, 7 |
| One patient, two overlapping free slots (case B) | `Refused(OVERLAPPING)`; patient holds exactly one of the two; the loser's slot stays free | D-32, PRD req 3, 4, 7 |
| Same patient, same slot, twice at once | `Refused(TAKEN)`, not `OVERLAPPING` (an own-held slot is taken; taken comes before overlap); one booking | `book-a-slot` PRD req 11, D-11, D-21, D-31 |
| Three or more patients, same slot | one `Booked`, every other `Refused(TAKEN)` | PRD scope ("the same rule" beyond two), D-31 |
| One patient, three or more mutually overlapping slots | one `Booked`, every other `Refused(OVERLAPPING)`; patient holds one | PRD scope, D-32 |
| Overlapping slots that are not all mutually overlapping (chain: first and third do not overlap) | not "exactly one": the outcome is any outcome of some sequential order (e.g. first and third both `Booked`, the middle `OVERLAPPING`) | PRD section 2 (measure) |
| Slot has started by the time the loser is judged (past and taken, past and overlapping) | `Refused(PAST)`, not `TAKEN` / `OVERLAPPING`; the winner stays `Booked` (judged earlier) | PRD req 5, D-21 |
| Unknown slot (unknown and taken) | `Refused(UNKNOWN_SLOT)` for every request on it; an unknown slot has no booking, so it is never "taken"; a valid request on a known slot at the same time is `Booked` | D-21 |
| Missing identifier (blank and taken) | `Refused(MISSING_IDENTIFIER)`, never `TAKEN`; the valid request on the slot is `Booked`; two missing requests both `MISSING_IDENTIFIER`; nothing stored for them | D-34, PRD req 5 |
| Loser who also holds a slot overlapping the contested slot (C holds X; C and B race for S, X overlaps S) | `TAKEN` if B was judged first, `OVERLAPPING` if C was; B is `Booked` either way. Both are outcomes of a sequential order | PRD section 2, D-21, D-35 |
| What the winner sees | `Booked(Booking(winner, slot))`, equal to what a lone booking returns, and equal to the booking the store then holds | PRD req 7 |
| Effect of a refused call on the store | none: later calls behave as if it never happened (the loser's patient can book another free slot; the loser's overlapping slot is still bookable by someone else; asking the loser's request again gives the same refusal) | PRD req 7, `book-a-slot` req 12 |

Flag for the human (decided by documents, but a person may not have read it): in the loser-who-holds-an-overlap row, the third party sees `TAKEN` or `OVERLAPPING` depending on arrival. D-31 says the same-slot loser sees `TAKEN`; this row is the one case where a refused request gets either of two reasons. If the human wants `TAKEN` in every order, that is a new product rule (it would change the D-21 order), not a change here.

### Caller-visible list for this plan

The plan adds no operation, parameter or type, so the list is the situations above plus: called twice by the same patient (row 3, and a repeat after the race: same refusal, nothing changed); called with nothing or an invalid value (rows "unknown" and "missing identifier"); edge of the range (a slot starting exactly now is bookable, D-19: unchanged, not a simultaneity question); different order (any request may win: row "chain", PRD req 6). Nothing is left to a choice.

## 1. Metadata
- **Type**: feature (edge case of `book-a-slot`)
- **Date**: 2026-10-18
- **Status**: in-progress

## 2. Goal

Prove, with tests that cannot pass by luck, that when requests to book arrive at the same moment exactly one wins each conflict and every other request is refused with the reason it would get had it come right after, and that a refusal changes nothing.

## 3. Context

- Code: `BookSlot.book` runs inside `store.atomically`: reads the clock, gathers facts (`findSlot`, `activeBookingOf`, `slotsHeldBy`), calls `BookingRule.decide`, saves on `Booked`. `InMemoryBookingStore` uses one `ReentrantLock` for `atomically` and for each read and write. The clock is read inside the unit, so the moment judged is the moment after the winner.
- Tests: `BookSlotConcurrencyTest` has two tests asserting `size() <= 1` (which also passes with zero bookings) and a decorator `MeetingStore` whose `save` waits up to 500 ms for both attempts to have read. Weakness: on a very slow machine the wait can end before the second attempt reads, the first saves, the second then sees `TAKEN`, and the test passes without the lock. The wait also always burns 500 ms when the lock works.
- The lock lives in `adapters`; INV-003 (PIT) covers `domain` and `application` only, so removing the lock is invisible to the mutation run.
- Invariants: INV-001 (no production dependency change; only a Javadoc is added); INV-002 (each test needs a test-case and each test-case an existing test: one test-case file per new test method); INV-003 (no domain or application change: nothing to mutate; no threshold, no baseline: human decision, unchanged).
- Harness: `bash tools/harness/run_all.sh`; Maven offline `-o` via `tools/harness/_maven.sh`. No `.plans/FEEDBACK.md`. Carried over: no major. Minor 1 (500 ms wait) is closed by this plan; minor 2 (loser pinned by no test) is the object of this plan; minor 3 (no mutation baseline) stays a human decision.
- Sensitive zones: nothing is stored or exposed in a new way.

## 4. Expected behaviors

Test boundary for all: the use case `BookSlot` over an `InMemoryBookingStore` wrapped by the test-only race gate (see "Technical choices"), in `BookSlotConcurrencyTest`; outcomes are read from `book`, effects through the store port (`activeBookingOf`, `slotsHeldBy`). Fixed `Clock` unless said. Constants of the file (`A`, `B`, `S`, `S2`), plus `C` and `S3`. No test says who wins: the winner is the request whose outcome is `Booked`.

1. **Same-slot loser (PRD req 1, 2, 7; D-31, D-35).** Given a free future slot, when A and B book it at the same moment, then exactly one outcome is `Booked(Booking(winner, S))` and the other is `Refused(TAKEN)`; `activeBookingOf(S)` is the winner's booking; the loser's patient holds nothing. Method `oneOfTwoSimultaneousBookingsOfASlotWinsAndTheOtherSeesTaken` (replaces `twoSimultaneousBookingsOfOneSlotNeverBothSucceed`).
2. **Overlapping loser (PRD req 3, 4, 7; D-32).** Given two free overlapping slots of two practitioners, when A books both at the same moment, then exactly one `Booked` and the other `Refused(OVERLAPPING)`; A holds exactly the winner's slot; the loser's slot has no booking. Method `oneOfTwoSimultaneousOverlappingBookingsOfAPatientWinsAndTheOtherSeesOverlapping` (replaces `twoSimultaneousOverlappingBookingsByOnePatientNeverBothSucceed`).
3. **Same patient, same slot twice (D-11, D-21, D-31).** When A books S twice at the same moment, then one `Booked`, the other `Refused(TAKEN)` (never `OVERLAPPING`), one booking. Method `aPatientBookingTheSameSlotTwiceAtOnceSeesTakenForTheOther`.
4. **Three or more callers, same rule.** Same slot with five patients: one `Booked`, four `Refused(TAKEN)`. Three mutually overlapping slots for one patient: one `Booked`, two `Refused(OVERLAPPING)`, one slot held. Method `manySimultaneousBookingsLeaveOneWinnerAndTheRestRefusedForTheSameReason`.
5. **Outcome could have happened in sequence (PRD section 2).** For each scenario below, the vector of outcomes of the concurrent run is one of the vectors obtained by running the same requests one after the other, on a fresh store, in every possible order (computed by the test through `BookSlot`, no hard-coded list), and the bookings left in the store equal those of the matching sequential run. Scenarios: (a) A books S and S2 (overlapping) while B books S2; (b) A books a chain S1 (60-120), S2 (90-150), S3 (130-190) (S1 and S3 do not overlap); (c) C already holds X overlapping S, then B and C book S at the same moment (accepts `TAKEN` or `OVERLAPPING` for C, `Booked` for B). Method `aSimultaneousOutcomeIsOneThatSomeOrderOneAfterTheOtherWouldGive`.
6. **Past comes before taken and overlapping (PRD req 5, D-21).** Given a clock that moves to after the slot's start the moment the winner is saved, when two patients book the same slot at the same moment, then the winner is `Booked` and the loser `Refused(PAST)`; likewise for one patient booking two overlapping slots (loser `PAST`, not `OVERLAPPING`). Method `aLoserJudgedAfterTheSlotHasStartedSeesPastNotTakenOrOverlapping`.
7. **Unknown slot (D-21).** A and B book an unknown slot at the same moment: both `Refused(UNKNOWN_SLOT)`, nothing stored. With C booking the known slot S at the same time: C is `Booked`. Method `simultaneousBookingsOfAnUnknownSlotAreAllRefusedAsUnknown`.
8. **Missing identifier (D-34, PRD req 5).** A books S while a blank-patient request and an absent-slot-identifier request run at the same moment: A is `Booked`, both others `Refused(MISSING_IDENTIFIER)` (not `TAKEN`); two blank requests at the same moment are both `MISSING_IDENTIFIER`; the store holds only A's booking. Method `aMissingIdentifierIsReportedAsMissingWhileSomeoneElseBooksTheSlot`.
9. **A refusal changes nothing, the winner is unaffected (PRD req 7; req 12 of `book-a-slot`).** After a case A race: the winner's outcome equals the booking in the store; the loser's patient can then book another free slot (`Booked`); asking the loser's request again gives `Refused(TAKEN)` and changes nothing. After a case B race: the loser's slot, still free, can be booked by another patient (`Booked`). Method `aRefusedSimultaneousBookingLeavesNothingBehind`.

Order of calls: tests 4, 5 and 8 run requests in an unspecified order by design; their assertions hold for any order.

## 5. Steps

Test first. The code already satisfies the PRD, so new tests are expected green at once; their red is obtained by removing the lock (Step 5), which is the proof they test something.

- [ ] Step 1: in `src/test/java/io/example/medical`, replace `MeetingStore` and `runTogether` of `BookSlotConcurrencyTest` with a race helper (a new test-support class `Race` and the gate decorator, see "Technical choices") that starts N attempts on N `Thread`s, forms the dangerous interleaving without any timed wait, and returns the outcomes in request order. The 10 s limit stays only as a failure guard.
- [ ] Step 2: write tests 1 and 2 on the helper (they replace the two existing tests); run them green.
- [ ] Step 3: write tests 3 to 9 one at a time, each green before the next. Test 5 needs a helper `sequentialOutcomes(slots, preBookings, requests)` that replays every permutation on a fresh `InMemoryBookingStore`. Test 6 needs a movable test clock (an `AtomicReference<Instant>`) flipped by a hook on the decorator's `save`.
- [ ] Step 4: write the test-cases below; update the Javadoc of `BookSlotConcurrencyTest` (it no longer says nothing about the loser). In `BookingStore`, add one sentence to the Javadoc of `atomically`: the unit is atomic among units run on the same store instance in one process; making it hold across processes (a shared database) is the adapter's job. No other production change.
- [ ] Step 5 (lock-removal proof, not committed): follow "How the developer shows that removing the lock makes a test fail", then restore.
- [ ] Step 6: full `mvn -o test` through `tools/harness/_maven.sh`, then `bash tools/harness/run_all.sh` (INV-001, INV-002 green). No mutation run needed (no `domain` or `application` change; PIT does not cover the adapter): say so in the report.

### Business test-cases (docs/business/test-cases/book-a-slot/)

Common: `feature: book-a-slot`, `type: functional`, `status: covered`, `automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::<method>`; bodies in given / when / then business words, no class names.

| File | priority | method | source |
|---|---|---|---|
| `simultaneous-bookings-never-double-book.md` (rewritten: the other patient is refused as taken) | high | `oneOfTwoSimultaneousBookingsOfASlotWinsAndTheOtherSeesTaken` | PRD edge-simultaneous req 1, 2, 7; D-31 |
| `simultaneous-overlapping-bookings-loser-sees-overlapping.md` | high | `oneOfTwoSimultaneousOverlappingBookingsOfAPatientWinsAndTheOtherSeesOverlapping` | req 3, 4, 7; D-32 |
| `simultaneous-same-patient-same-slot-loser-sees-taken.md` | medium | `aPatientBookingTheSameSlotTwiceAtOnceSeesTakenForTheOther` | `book-a-slot` req 11; D-11, D-21 |
| `many-simultaneous-bookings-one-winner.md` | medium | `manySimultaneousBookingsLeaveOneWinnerAndTheRestRefusedForTheSameReason` | PRD scope; D-31, D-32 |
| `simultaneous-outcome-matches-some-order-one-after-the-other.md` | high | `aSimultaneousOutcomeIsOneThatSomeOrderOneAfterTheOtherWouldGive` | PRD section 2 |
| `simultaneous-past-slot-loser-sees-past.md` | high | `aLoserJudgedAfterTheSlotHasStartedSeesPastNotTakenOrOverlapping` | req 5; D-21 |
| `simultaneous-unknown-slot-refused-as-unknown.md` | medium | `simultaneousBookingsOfAnUnknownSlotAreAllRefusedAsUnknown` | D-21 |
| `simultaneous-missing-identifier-refused-as-missing.md` | medium | `aMissingIdentifierIsReportedAsMissingWhileSomeoneElseBooksTheSlot` | D-34; req 5 |
| `simultaneous-refusal-leaves-nothing-behind.md` | high | `aRefusedSimultaneousBookingLeavesNothingBehind` | req 7; `book-a-slot` req 12 |

The first file loses its sentence "What the other patient is shown is not specified yet." and says the other patient is refused as taken, and that either patient may be the one who books.

## 6. Risks & edge cases

- **Tests that pass by luck.** A race test written with a timed wait or a bare start latch can pass without the lock. Every lock-sensitive test (1 to 6) must go through the gate and must fail with the lock removed (Step 5).
- **Which request wins is not guaranteed (D-35).** A test that expects patient A to win is wrong and flaky. Assert on the outcome type and the reason, and derive the winner from the outcomes.
- **Gate false positives.** A thread must count as "held back by the lock" only after it has entered `atomically`; before that, a thread waiting on the start latch also looks parked. See the technical choice.
- **The clock flip (test 6)** happens inside the winner's `save`, i.e. inside the unit, so the loser reads the clock after it. It proves the clock is read inside the unit in the common interleaving; a clock read hoisted before the unit but after another request's save would need a third interleaving: accepted limit, named in the report.
- **Test 5 oracle uses `BookSlot` itself** run in sequence. It proves concurrent = sequential, not that the sequential rule is right (that is `BookSlotTest`).
- **Per process only.** The guarantee holds for one store instance in one process. Out of scope; one sentence of Javadoc records it.
- **Test duration.** No sleep and no timed wait in the normal path; a test that takes seconds means the gate never opened (it fails with a message after the guard).
- **Mutation:** nothing to run, see Step 6.

## 7. Out of scope

Performance and fairness; callers retrying on their own; how the exclusion is built (lock versus another mechanism); several processes or a database; blank identifiers beyond the combination in test 8 (done by `edge-blank-ids`); a mutation threshold or baseline (human decision); any change to `BookingRule`, `BookSlot` or `InMemoryBookingStore` code.

## 8. Deviations

(none)

## 9. Self-review

(filled at closing)

## 10. Follow-up actions

(filled at closing)

## Technical choices (no caller can observe them; for the reviewer to challenge)

- **The 500 ms wait is dropped, not kept.** Reason: it decides the result by wall-clock time, so a slow machine can pass a test without the lock. Replacement: a condition gate, below.
- **The gate.** A test-only `BookingStore` decorator, one per race, wraps a real `InMemoryBookingStore`. A thread is "at the door" once it has called `atomically`, and "arrived" once it returns from `slotsHeldBy` (the last read of `decide`). After its reads, a thread waits at the gate until every other thread of the race has entered the door and is either arrived, parked or blocked on a lock (`Thread.getState()` is `WAITING` or `BLOCKED`), or finished. It spins with `Thread.onSpinWait()`; a 10 s `nanoTime` limit exists only to fail with a clear message ("the race never formed"). With the lock: the first thread holds it at the gate, the others park on it, the gate opens, the first saves, the others follow in turn. Without the lock: all threads reach the gate having read the same state, then all decide and save: the double booking is certain, not likely. Attempts run on plain `Thread`s (not a pool) so that `TERMINATED` means finished. A request that skips the store (missing identifier) simply finishes. No randomness, no `sleep`.
- **Clock for test 6.** A movable test clock flipped by a hook of the decorator's `save`, not a second clock implementation in `src/main`.
- **Test 5 oracle.** Every permutation of at most four requests is replayed on a fresh store through `BookSlot`; outcome vector and final bookings compared with the concurrent run. No expected values written by hand.
- **Weak assertions removed.** `size() <= 1` becomes "exactly one `Booked`": a run in which nobody books now fails.
- **Layout.** New tests stay in `BookSlotConcurrencyTest`; the helper (`Race` and the decorator) sits in the test tree next to it, not in `src/main`. `ArchitectureTest` and the layering are unaffected. Splitting the helper into its own file is allowed if the test file grows too large.
- **Javadoc only in production**, on the port `BookingStore.atomically` (not in `invariants.md`, which lists harness checks).

## How the developer shows that removing the lock makes a test fail

Done by hand, not committed, and reported in the developer's hand-off (what was changed, which tests failed, with their messages).

1. Green baseline: run `BookSlotConcurrencyTest` ten times in a row (temporarily `@RepeatedTest(10)` or a shell loop): all pass, with no 500 ms wait in any test.
2. Mutation 1, the realistic bug: in `InMemoryBookingStore.atomically`, replace the body by `return unit.get();` (the per-method locks stay). Run the class ten times. Required: tests 1 to 6 fail on every one of the ten runs, with a message about two bookings of one slot, two overlapping slots, a loser not refused, or an outcome no order explains. Tests 7, 8 and 9 do not depend on exclusion and may stay green: say so.
3. Mutation 2, stricter: also make `save` a plain unlocked `put`. Same expectation.
4. Restore the file (`git diff` on `src/main` shows only the Javadoc sentence), re-run the ten rounds green, then Step 6.
5. If any of tests 1 to 6 passes in any mutated run, the gate is wrong: that is a failing step, not a deviation to accept.
