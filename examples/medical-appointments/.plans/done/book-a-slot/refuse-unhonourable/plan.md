---
role: planner
status: done
reasons: []
---

# Plan: refuse a booking that cannot be honoured (story 2)

Skill announced: `plan-driven-dev` (context and plan steps only). All consumer-visible points are settled.

## Answers applied

Round 1: D-27, D-28. Round 2: D-29 (answered-by-delegate): an invalid range is rejected at creation with `IllegalArgumentException`. No question remains.

## Decisions applied (decisions.md, architect.md)

- D-25 / D-26: result is `Booked(Booking)` or `Refused(reason)`; reasons `UNKNOWN_SLOT`, `PAST`, `TAKEN`, `OVERLAPPING` already exist; this story makes the last three producible.
- D-21 and criteria 9-10: one order, in one place (`BookingRule`): unknown, past, taken (own-held included), overlap. Pairs: unknown with anything is unknown; past and taken is past; past and overlap is past; taken and overlap is taken.
- D-19: a slot starting exactly now is bookable. D-20: back-to-back slots do not overlap. D-10: several bookings per patient, with one or several practitioners, if they do not overlap.
- Architect: the current moment is an instant passed to the rule; the use case reads an injected `Clock`. Value object time range with `start < otherEnd && otherStart < end`. "Free" is derived; the store port answers "slot by id", "active booking of a slot", "slots held by a patient".
- D-22 still deferred: empty, blank or absent identifiers (including `null`): no check, no test, unspecified.
- D-27 (criterion 11): a range is valid only if end is strictly after start; zero-length, inverted or absent is rejected at creation. D-28 (criterion 12): overlapping slots of one practitioner may be booked by different patients; the overlap rule is per patient.
- Simultaneous booking of one slot: the outcome seen by the loser is NOT decided here (see M1 below).

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress

## 2. Goal

A booking is refused, with a clear reason, when the slot does not exist, starts before the current moment, is already taken, or overlaps in time a slot the same patient holds. A slot starting exactly now and slots back to back can be booked. A refusal changes nothing. The patient may hold several bookings that do not overlap. Story 2 also closes the two majors carried over from story 1 (M1, M2).

## 3. Context

- Code from story 1 (hexagonal, ADR-0001): `domain` (`PatientId`, `SlotId`, `PractitionerId`, `Slot(id, practitioner)`, `Booking(patient, slot)`, `BookingOutcome`, `RefusalReason`, `BookingRule.decide(patient, slot, activeBookingOnSlot)`), `application` (`BookSlot`, port `BookingStore` with `findSlot`, `activeBookingOf`, `save`, `atomically`), `adapters` (`InMemoryBookingStore`, one `ReentrantLock`). Tests: `BookSlotTest` (7 tests, slots built without time), `ArchitectureTest`.
- Today `BookSlot.book` calls `findSlot(...).orElseThrow()` (M2) and `BookingRule` only knows "taken".
- Applicable invariants: INV-001 (`domain` imports only `java.*`; `application` imports `domain` and the JDK only; `java.time.Instant`, `Clock`, `Duration` are JDK, so allowed; no import of `adapters` from them); INV-002 (each test-case points at an existing test method; each test class has a test-case; test-cases need `feature`, `type`, `priority`, `automated_test`, `status`, plus a source line); INV-003 (PIT on `domain` and `application`, no threshold, warn; the boundaries `<` vs `<=` of past and overlap are the likely survivors). Sensitive zones: the in-memory adapter already exists and stays in memory with ids only; no persistence or exposure is added.
- Harness before each commit: `bash tools/harness/run_all.sh`; mutation: `bash tools/harness/run_mutation.sh --scope diff`. Maven as in the brief, offline `-o`.
- Test-case format (from `check_test_coverage.py` and story 1): a file under `docs/business/test-cases/book-a-slot/` with front-matter `feature`, `type: functional`, `priority`, `source`, `automated_test: src/test/java/io/example/medical/<Class>Test.java::<method>`, `status: covered`; the method name must appear in the file; each test class needs at least one test-case.
- No `.plans/FEEDBACK.md`: no lesson. Story 1 review (GO, two open majors) read.

## 4. Expected behaviors

Test boundary for all of them, unless stated: the use case `BookSlot` (module API of `application`), built on `InMemoryBookingStore` seeded with slots, and a fixed `Clock` (`Clock.fixed`) passed to `BookSlot`. Effects are read through the store port (`activeBookingOf`, and `slotsHeldBy` for a patient). Tests live in package `io.example.medical`. Notation: NOW is the fixed instant; slots are built at offsets from NOW.

Existing story 1 tests are kept and adapted only for the new constructor argument (clock) and slots with a time range placed after NOW; their test-cases do not change.

### Unknown slot
- **Criterion 1**: given a store without slot X, when patient A books X, then `Refused(UNKNOWN_SLOT)` and nothing is stored. Method `refusesAnUnknownSlot`. Replaces the exception of M2.
- Nothing / twice: booking the unknown slot twice gives the same refusal, still nothing stored (inside the same test).

### Past, current moment
- **Criterion 2**: given a slot starting one nanosecond before NOW, when A books it, then `Refused(PAST)`. Method `refusesASlotStartingBeforeNow`. The far-past slot (hours before) is in the same test.
- **Criterion 3 (edge)**: given a slot starting exactly at NOW, when A books it, then `Booked`. Method `booksASlotStartingExactlyNow`. Together with the previous test, they pin `<` against `<=`. A slot starting one nanosecond after NOW is booked (same test).
- The slot is in the past by its start only: a slot started but not yet ended is refused (req 7); covered by the 1 ns case.

### Several bookings, overlap
- **Criterion 4**: given A holds a slot, when A books a second slot that does not overlap it (with the same practitioner, then with another practitioner), then `Booked` and A holds both. Method `aPatientHoldsSeveralSlotsThatDoNotOverlap`.
- **Criterion 5**: given A holds slot S1 of practitioner P1, when A books slot S2 of practitioner P2 that overlaps S1, then `Refused(OVERLAPPING)`. Method `refusesASlotOverlappingOneThePatientHolds`. A different patient B can book S2 (the clash is per patient).
- **Criterion 12 (D-28)**: given two overlapping slots of the same practitioner, when patient A books one and patient B the other, then both are `Booked`. Method `overlappingSlotsOfOnePractitionerCanBeBookedByDifferentPatients`.
- **Criterion 6 (edge, shapes)**: given A holds a slot, then each of these booked by A is refused as overlapping: starts inside and ends after; starts before and ends inside; contains the held slot; is contained in it; has the same range; overlaps by one nanosecond. Method `overlapMeansSharingAStretchOfTime` (one test, a fixed list of cases, a failure message per case).
- **Criterion 7 (edge, back to back)**: given A holds a slot, then a slot starting exactly when it ends, and a slot ending exactly when it starts, are both booked. Method `backToBackSlotsDoNotOverlap`.
- Order of calls (different order): booking S1 then S2, or S2 then S1, gives the same outcomes (overlap is symmetric). Inside `refusesASlotOverlappingOneThePatientHolds`: both orders.

### Refusals change nothing
- **Criterion 8**: given a store with several bookings, after a refusal for unknown, past, then overlapping slot, the bookings of every slot are exactly as before: no new booking, no slot changes owner, the patient's held slots are the same. Method `anUnhonourableRefusalChangesNothing` (compares a snapshot of all slots before and after).

### Order of refusals
- **Criterion 9 and 10**, one test per pair family; each asserts the reason, and nothing changes:
  - unknown with any other rule: given patient A holds slots and the clock is after all of them, when A books an absent slot, then `UNKNOWN_SLOT`. Method `reportsUnknownBeforeAnyOtherRefusal`.
  - past before taken and overlap: given a past slot that is held by B (taken), and also overlaps a slot A holds, when A books it, then `PAST`; same for past and taken alone, past and overlap alone. Method `reportsPastBeforeTakenAndOverlap`.
  - taken before overlap: given a slot held by B that overlaps a slot A holds, when A books it, then `TAKEN`; given A books a slot A already holds (which overlaps itself), then `TAKEN`. Method `reportsTakenBeforeOverlap`.
  - A slot that breaks one rule only gets that reason (covered by the tests above).

### Time range (D-27, criterion 11)
- Given a start and an end, when the range is created with end after start, then it exists; with end equal to start, or before start, creation is rejected (`IllegalArgumentException`). Boundary: the domain API `TimeRange` (no use case creates slots in this feature). One nanosecond after start is accepted. Method `aRangeEndingNotAfterItsStartIsRejected` in `TimeRangeTest`. Absent bound (`null`): rejected too (same exception type, D-29), tested for start and for end.

### Atomicity (M1, without deciding the loser's outcome)
- Given two threads that book the same free slot at the same moment (patients A and B), then: at most one outcome is `Booked`, and the store holds at most one booking on that slot, equal to the one reported booked. The test does not inspect the other thread's outcome (neither its type nor its reason); that is the open product question. Method `twoSimultaneousBookingsOfOneSlotNeverBothSucceed` in `BookSlotConcurrencyTest`.
- Same for one patient booking two overlapping slots at the same moment: at most one `Booked`, and the patient holds at most one of the two. Method `twoSimultaneousOverlappingBookingsByOnePatientNeverBothSucceed`.
- Technique (not observable by callers): the test wraps the store in a test-only decorator whose `save` waits, for a bounded time, until a second thread has read the slot, so that without the lock both threads would have passed the check before any save. With the lock the wait times out and the test passes; without it both bookings succeed and the test fails. Deterministic, not a race of chance. To be verified by the developer: remove the lock in `atomically` locally, see both tests fail, restore it (not committed).

## 5. Steps

Test first for each behavior, then the minimum code, then invariants. Test-case and test created together.

- [ ] Step 1: add `TimeRange(Instant start, Instant end)` in `domain` (record) with `overlaps(TimeRange)` (`start < otherEnd && otherStart < end`) and the validation of the compact constructor (D-27: end strictly after start, no absent bound; exception type `IllegalArgumentException`, D-29). Driven by `aRangeEndingNotAfterItsStartIsRejected` and the overlap tests.
- [ ] Step 2: change `Slot` to `Slot(SlotId id, PractitionerId practitioner, TimeRange range)` in `domain`; update the slots in `BookSlotTest` (placed after NOW) and keep its 7 tests green with a fixed `Clock` argument to `BookSlot`.
- [ ] Step 3: add to the port `BookingStore` the operation `List<Slot> slotsHeldBy(PatientId)`; implement it in `InMemoryBookingStore` under the lock (booked slots whose booking belongs to the patient).
- [ ] Step 4: change `BookingRule.decide` to `decide(PatientId patient, Optional<Slot> slot, Instant now, Optional<Booking> activeBookingOnSlot, List<Slot> slotsHeldByPatient)`; checks in this order and nowhere else: slot absent -> `UNKNOWN_SLOT`; `slot.range().start() < now` -> `PAST`; active booking present -> `TAKEN`; any held slot whose range overlaps -> `OVERLAPPING`; else `Booked`. Driven one test at a time: unknown (`refusesAnUnknownSlot`), past, now, then taken stays green, then overlap, back to back, shapes, order tests, the snapshot test.
- [ ] Step 5: change `BookSlot` to take a `Clock` (`new BookSlot(store, clock)`); in `book`, inside `atomically`, read `clock.instant()` once, gather `findSlot`, `activeBookingOf` and `slotsHeldBy`, call `decide`, save on `Booked`. Remove `orElseThrow()` (M2). It still never orders or re-checks refusals.
- [ ] Step 6: write `BookSlotConcurrencyTest` with the decorator and the two atomicity tests; verify manually that removing the lock makes them fail (M1). Add a comment on `findSlot` in `InMemoryBookingStore` saying it reads without the lock because slots are fixed after construction (minor of the review).
- [ ] Step 7: tighten `slotIsNoLongerFreeAfterBooking` so that it asserts the exact booking, not only `isPresent()` (minor of the review); its test-case is unchanged.
- [ ] Step 8: write the business test-cases below under `docs/business/test-cases/book-a-slot/`.
- [ ] Step 9: run `bash tools/harness/run_all.sh` (INV-001, INV-002 green), then `bash tools/harness/run_mutation.sh --scope diff`; for each surviving mutant in `domain` or `application`, add a test of the missing behavior or justify an exclusion in `pom.xml`. Do not record a threshold or a baseline (human decision).

### Business test-cases (docs/business/test-cases/book-a-slot/)

Common: `feature: book-a-slot`, `type: functional`, `status: covered`, `automated_test: src/test/java/io/example/medical/<Class>.java::<method>`; body given / when / then in business words, no class names.

| File | priority | automated_test | source |
|---|---|---|---|
| `refuse-unknown-slot.md` | high | `BookSlotTest.java::refusesAnUnknownSlot` | PRD req 6, D-26; story 2 criterion 1 |
| `refuse-slot-already-started.md` | high | `BookSlotTest.java::refusesASlotStartingBeforeNow` | PRD req 7, D-9; criterion 2 |
| `book-slot-starting-now.md` | high | `BookSlotTest.java::booksASlotStartingExactlyNow` | PRD req 7, D-19; criterion 3 |
| `patient-holds-several-slots.md` | high | `BookSlotTest.java::aPatientHoldsSeveralSlotsThatDoNotOverlap` | PRD req 8, D-10; criterion 4 |
| `refuse-slot-overlapping-own-booking.md` | high | `BookSlotTest.java::refusesASlotOverlappingOneThePatientHolds` | PRD req 9, D-10; criterion 5 |
| `overlap-means-shared-stretch-of-time.md` | high | `BookSlotTest.java::overlapMeansSharingAStretchOfTime` | PRD req 10; criterion 6 |
| `back-to-back-slots-do-not-overlap.md` | high | `BookSlotTest.java::backToBackSlotsDoNotOverlap` | PRD req 10, D-20; criterion 7 |
| `unhonourable-refusal-changes-nothing.md` | high | `BookSlotTest.java::anUnhonourableRefusalChangesNothing` | PRD req 12, 4; criterion 8 |
| `refusal-order-unknown-first.md` | high | `BookSlotTest.java::reportsUnknownBeforeAnyOtherRefusal` | D-21; criteria 9, 10 |
| `refusal-order-past-before-taken-and-overlap.md` | high | `BookSlotTest.java::reportsPastBeforeTakenAndOverlap` | D-21; criteria 9, 10 |
| `refusal-order-taken-before-overlap.md` | high | `BookSlotTest.java::reportsTakenBeforeOverlap` | D-21, PRD req 11; criteria 9, 10 |
| `slot-range-must-end-after-start.md` | medium | `TimeRangeTest.java::aRangeEndingNotAfterItsStartIsRejected` | D-27; criterion 11 |
| `overlapping-slots-of-one-practitioner.md` | medium | `BookSlotTest.java::overlappingSlotsOfOnePractitionerCanBeBookedByDifferentPatients` | D-28; criterion 12 |
| `simultaneous-bookings-never-double-book.md` | high | `BookSlotConcurrencyTest.java::twoSimultaneousBookingsOfOneSlotNeverBothSucceed` | PRD req 5 only |
| `simultaneous-overlapping-bookings-never-both-succeed.md` | high | `BookSlotConcurrencyTest.java::twoSimultaneousOverlappingBookingsByOnePatientNeverBothSucceed` | PRD req 5, 9 only |

The two simultaneity test-cases state only that a slot (or a patient's overlapping slots) never ends up with two bookings; they say in their body that the outcome shown to the other person is not specified yet.

## 6. Risks & edge cases

- **M1, atomicity.** Planned as a test that asserts req 5 and 9 under simultaneity and says nothing about the loser. If the human prefers that even this wait for the edge-case request, say so: the two tests and their test-cases are then dropped, the gap stays reported. Not decided by this plan either way.
- **PIT does not cover the lock** (it lives in `adapters`, outside INV-003 scope): the proof is the test plus the manual check of step 6. Widening the PIT scope is a human decision, not taken here.
- Mutation: the boundaries of "past" (`<` vs `<=`) and "overlap" (`<` vs `<=`, one side only) and the order of checks are the likely survivors; the 1 ns cases, back-to-back both sides and the pair tests aim at them.
- A held slot that is itself in the past can overlap a new slot only if it is still running, which a booking of a future-or-now slot cannot reach in practice; no special case, held slots are not filtered by time.
- `null` identifiers or a `null` clock: unspecified (D-22), no test. A `null` time bound is rejected (D-27).
- Existing tests must move their slots after NOW; a test that forgets would show `PAST`.
- Two overlapping slots of one practitioner booked by different patients: allowed (D-28), tested.

## 7. Out of scope

Outcome of simultaneous booking seen by the loser; empty, blank or absent identifiers (D-22); listing free slots (F1.1), cancellation (F3.1), how slots are preloaded and the consistency of a practitioner's agenda (F4.1, D-28); mutation threshold or baseline for INV-003 and the widening of its scope (human decisions); persistence beyond memory.

## 8. Deviations

(none)

## 9. Self-review

(filled at closing)

## 10. Follow-up actions

(filled at closing)

## Technical choices (no caller can observe them; for the reviewer to challenge)

- `TimeRange` as a record in `domain` holding `Instant`s; `Slot` a record carrying it; no `Duration` field.
- `BookingRule` stays a stateless class, one `decide` method that is the only place where refusals are ordered; the facts (slot or absence, the instant, the active booking on the slot, the slots held by the patient) are given as parameters.
- One port `BookingStore` extended with `slotsHeldBy`; the held slots are found by scanning the bookings in the in-memory adapter (a database would index by patient).
- The clock is read once per attempt, inside the atomic unit, so one attempt sees one moment.
- Fixed `Clock` in tests; no mocking framework; the concurrency decorator is a test-only class, local to `BookSlotConcurrencyTest`.
- Rejection of an invalid range (D-29) is an `IllegalArgumentException` at creation, since only whoever loads the slots can meet it, not a patient booking.
