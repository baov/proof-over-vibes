---
role: planner
status: done
reasons: []
---

# Plan: book a free slot, and never double-book it (story 1)

## Decisions applied (answers.md, decisions.md)

- D-25: a refusal is a typed result: `Booked(Booking)` or `Refused(RefusalReason)`.
- D-26: reasons `UNKNOWN_SLOT`, `PAST`, `TAKEN`, `OVERLAPPING`; story 1 produces only `TAKEN`.
- D-22: empty, blank or absent identifiers deferred: no check, no test, no test-case, behavior unspecified (stories.md open point 2 stays open).
- Already settled by documents: rebooking by the same patient and a second patient on a taken slot are `TAKEN` (D-11, criteria 3-4); refusal order is D-21 (story 2). Nothing consumer-visible remains open for story 1.

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress

## 2. Goal

A patient books a free slot of a practitioner: the booking links that patient to that slot and the slot is no longer free. A slot that already has a booking, whoever holds it, is refused and nothing changes; a slot never has more than one active booking. Unknown, past and overlapping slots are story 2.

## 3. Context

- Greenfield: no feature code, only `pom.xml` (Java 21, JUnit 5, ArchUnit, PIT, base package `io.example.medical`) and `ArchitectureTest`. Packages `domain`, `application`, `adapters` under the base package (ADR-0001, hexagonal, accepted).
- Architect's decisions applied: ids as opaque value objects, no name or health data; "free" is derived (no active booking), not a stored flag; the rule is one sequence of checks in `domain` returning the first failure (D-21, only the "taken" check exists in story 1); check and save of the booking are one atomic unit through the store port, in-memory adapter with a single lock; the current moment and the overlap test belong to story 2.
- Applicable invariants: INV-001 (`domain` imports only the JDK; `application` imports `domain` and the JDK only; neither imports `adapters`; warn). INV-002 (every test-case points at an existing test, every test class has a test-case; broken reference is an error). INV-003 (PIT on `domain` and `application`, no threshold, warn). Sensitive zones: none touched (ids only, in memory).
- Harness before each commit: `bash tools/harness/run_all.sh`; mutation: `bash tools/harness/run_mutation.sh --scope diff`. Maven: see brief, offline `-o`.
- Test-case reference format: `automated_test: src/test/java/<path>/<Class>Test.java::<method>`; the bridge checks the method name appears in the file; the test class itself needs at least one test-case pointing at it.
- No `.plans/FEEDBACK.md` yet: no earlier lesson.

## 4. Expected behaviors

Test boundary for all of them: the use case `BookSlot` (module API of `application`), built on the in-memory store from `adapters`, seeded with a list of slots. The effect on a slot is read through the store port (`activeBookingOf(slotId)`); no query operation is added for callers (listing free slots is F1.1, out of scope). Tests live in package `io.example.medical` (ArchUnit analyses production classes only). Test class: `src/test/java/io/example/medical/BookSlotTest.java`.

- **Nominal, criterion 1**: given a free slot S, when patient A books S, then the outcome is "booked" and carries a booking of A on S, and the store holds that booking for S. Method `booksAFreeSlotForThePatient`.
- **Criterion 2**: given A booked S, then S has an active booking (it is no longer free). Method `slotIsNoLongerFreeAfterBooking`.
- **Criterion 3**: given S booked by A, when B books S, then the outcome is "refused" with reason `TAKEN`. Method `refusesASlotBookedByAnotherPatient`.
- **Criterion 4 (called twice)**: given S booked by A, when A books S again, then "refused" with reason `TAKEN`. Method `refusesASlotThePatientAlreadyHolds`.
- **Criterion 5**: given S booked by A, after B's refused attempt (and after A's own repeated attempt), the booking on S is still A's, unchanged, and S has exactly that one booking. Method `aTakenRefusalLeavesTheExistingBookingUnchanged`.
- **Criterion 6 (order)**: given several slots and several patients, for any sequence of sequential attempts (fixed list of sequences, mixing repeats, other patients and other slots), at the end every slot has at most one active booking, and the first successful attempt on a slot is the one that holds it. Method `aSlotNeverHoldsMoreThanOneBookingWhateverTheSequence`.
- **Edge, independence**: booking S leaves another slot S2 free and bookable by another patient (a booking affects its slot only). Method `bookingOneSlotLeavesOtherSlotsFree`. Source: req 1, 2, 5.
- Same patient, several different free slots: not tested here (story 2, req 8, brings the overlap question).
- Invalid / nothing: empty, blank or absent identifiers are not tested (D-22). An unknown slot id is story 2; see risks.

## 5. Steps

Each test is written red first, then the minimum code, then the invariants checked. Test-case and test are created in the same step.

- [ ] Step 1: create `domain` value objects `PatientId`, `SlotId`, `PractitionerId` (records wrapping a `String`, no validation, D-22) and entities `Slot(SlotId, PractitionerId)` and `Booking(PatientId, SlotId)`, all in `io.example.medical.domain`. No time range yet (story 2).
- [ ] Step 2: create `domain` types for the outcome, per D-25 and D-26: sealed `BookingOutcome` with `Booked(Booking)` and `Refused(RefusalReason)`, and enum `RefusalReason` with the four names of D-26.
- [ ] Step 3: create the domain rule `BookingRule` in `domain` with one method `decide(PatientId, Slot, Optional<Booking> activeBookingOnSlot)` returning the first failing reason or a booking; story 1 has the single check "taken" (an active booking exists, whoever holds it). This is the only place where refusals are ordered.
- [ ] Step 4: create the port `BookingStore` in `application` with `Optional<Slot> findSlot(SlotId)`, `Optional<Booking> activeBookingOf(SlotId)` and `<T> T atomically(Supplier<T>)` (the check-and-save is one unit), plus `save(Booking)`.
- [ ] Step 5: create the use case `BookSlot` in `application`: `BookingOutcome book(PatientId, SlotId)`; inside `atomically`, gather the slot and the active booking, call `BookingRule.decide`, save the booking if it is "booked". It only gathers facts; it never orders or re-checks refusals.
- [ ] Step 6: create `InMemoryBookingStore` in `adapters`, built from a list of `Slot`, with one lock around `atomically`; stores bookings by slot id.
- [ ] Step 7 (TDD loop, in this order): `booksAFreeSlotForThePatient`, `slotIsNoLongerFreeAfterBooking`, `refusesASlotBookedByAnotherPatient`, `refusesASlotThePatientAlreadyHolds`, `aTakenRefusalLeavesTheExistingBookingUnchanged`, `bookingOneSlotLeavesOtherSlotsFree`, `aSlotNeverHoldsMoreThanOneBookingWhateverTheSequence`. Steps 1-6 are created as these tests demand them, not ahead of them.
- [ ] Step 8: write the 7 business test-cases below under `docs/business/test-cases/book-a-slot/`, one file per case, each pointing at its method.
- [ ] Step 9: run `bash tools/harness/run_all.sh` (INV-001, INV-002 green), then `bash tools/harness/run_mutation.sh --scope diff`; for each surviving mutant, add a test of the missing behavior or justify an exclusion in `pom.xml`.

### Business test-cases (docs/business/test-cases/book-a-slot/)

Front-matter of each (the harness bridge fields):

| File | feature | priority | automated_test (method) | source |
|---|---|---|---|---|
| `book-free-slot.md` | book-a-slot | high | `BookSlotTest.java::booksAFreeSlotForThePatient` | PRD req 1; story 1 criterion 1 |
| `slot-not-free-after-booking.md` | book-a-slot | high | `::slotIsNoLongerFreeAfterBooking` | PRD req 2; story 1 criterion 2 |
| `refuse-slot-booked-by-another.md` | book-a-slot | high | `::refusesASlotBookedByAnotherPatient` | PRD req 3; story 1 criterion 3 |
| `refuse-slot-already-held.md` | book-a-slot | high | `::refusesASlotThePatientAlreadyHolds` | PRD req 11, D-11; story 1 criterion 4 |
| `refusal-leaves-booking-unchanged.md` | book-a-slot | high | `::aTakenRefusalLeavesTheExistingBookingUnchanged` | PRD req 4, 12; story 1 criterion 5 |
| `slot-never-has-two-bookings.md` | book-a-slot | high | `::aSlotNeverHoldsMoreThanOneBookingWhateverTheSequence` | PRD req 5; story 1 criterion 6 |
| `booking-one-slot-leaves-others-free.md` | book-a-slot | medium | `::bookingOneSlotLeavesOtherSlotsFree` | PRD req 1, 2, 5 |

Common to all: `type: functional`, `status: covered`, `automated_test: src/test/java/io/example/medical/BookSlotTest.java::<method>`, `source: <last column>`. Body: given / when / then in business words (patient, slot, booking, refused as taken), no class names.

## 6. Risks & edge cases

- Unknown slot id: story 2 (criterion 1) refuses it; story 1 must not invent a behavior for an absent slot. Until story 2, `BookSlot` on an unknown id is unspecified and untested; story 1 must not be released alone.
- Simultaneous booking of one slot: the mechanism (single atomic unit) is built, since requirement 5 needs it; what the losing caller sees is the open PRD question. No test asserts that outcome and none is planned. The sequential test in criterion 6 does not prove atomicity: INV-003 should show a surviving mutant if the lock is removed; this is the known gap, to say in the review.
- Mutation: the "taken" check and the save are the likely survivors (equality of ids, `Optional` handling); the sequence test is meant to kill them.
- Identifiers carry no validation (D-22): `null` ids will fail with an unspecified error until a request decides.

## 7. Out of scope

Unknown, past and overlapping refusals, the current moment, the time range and overlap test, and the D-21 order tests (story 2); simultaneous booking outcome; empty, blank or absent identifiers (D-22); validating that a slot's end is after its start (a question for story 2's plan, when the range appears); how slots are preloaded (F4.1); listing free slots (F1.1); cancellation; any storage beyond in-memory.

## 8. Deviations

(none)

## 9. Self-review

(filled at closing)

## 10. Follow-up actions

(filled at closing)

## Technical choices (no caller can observe them; for the reviewer to challenge)

- Ids are `String`-wrapping records; `Slot` and `Booking` are records; a booking has no id of its own (identified by patient and slot, since a slot has at most one active booking).
- `BookingRule` is a stateless class with a static or instance `decide` method; story 2 extends its parameters (slot absence, instant, bookings held by the patient) and adds checks in D-21 order.
- The port is a single `BookingStore` rather than two (slots, bookings): one atomic unit spans both. Split later if a second adapter needs it.
- `atomically` is a lock in the in-memory adapter (`ReentrantLock` or `synchronized`); a database adapter would map it to a transaction.
- Tests build the store through `new InMemoryBookingStore(List.of(...))`; no mocking framework (no dependency).
- Reads in tests go through the port rather than a new public use case.
