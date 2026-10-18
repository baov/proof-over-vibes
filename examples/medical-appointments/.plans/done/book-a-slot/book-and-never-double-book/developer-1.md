---
role: developer
status: done
reasons: []
---

# Developer note, iteration 1 (story 1: book and never double-book)

Skills announced: `plan-driven-dev` (implementation steps) and `behavior-driven-testing` (tests through the `BookSlot` use case, no mocks).

## Commits (branch claude/bank-account-poc-1435f8, only files under examples/medical-appointments)

1. `b8540b8` Book a free slot for a patient: domain types, `BookingOutcome`, `RefusalReason`, `BookingRule`, port `BookingStore`, `BookSlot`, `InMemoryBookingStore`, test and test-case 1. Red first (compilation failure), then green.
2. `9764d65` A booked slot is no longer free (test and test-case).
3. `552f718` Refuse a slot already booked by another patient. Red verified (booked instead of refused), then the "taken" check restored in `BookingRule`.
4. `72c4788` Same-patient refusal, refusal leaves booking unchanged, independence of slots, and the order/sequence test, with the 3 matching test-cases.
5. `8baeef1` Test-case of the sequence test (missing from commit 4: that commit left one orphan test for a moment).

## Honest notes on red/green

- Tests 2, 4, 5, 7 (`slotIsNoLongerFreeAfterBooking`, `refusesASlotThePatientAlreadyHolds`, `aTakenRefusalLeavesTheExistingBookingUnchanged`, `bookingOneSlotLeavesOtherSlotsFree`) and the sequence test passed on first run: the code from tests 1 and 3 already satisfied them. I did not rewrite code to force a red; they pin behavior. The mutation run is the evidence they protect something.
- The sequence test is sequential, as planned; it does not prove atomicity.

## Test-cases

7 files under `docs/business/test-cases/book-a-slot/`, each with feature, type, priority, source, `automated_test` (exact method of `BookSlotTest.java`) and status covered.

## Commands and results

- `mvn -o test` (Maven 3.9.9 under ~/.m2/wrapper): 7 tests, 0 failures. Includes ArchitectureTest (ArchUnit) rules.
- `bash tools/harness/run_all.sh --with-mutation`: INV-001 exit 0; INV-002 7 covered_ok, 0 broken, 0 orphan, exit 0; INV-003 exit 0; harness exit 0.
- Mutation (scope critical, PIT): score 100.0%, 7 killed / 7 generated, no survivors. No threshold written (human decision). Baseline not recorded in invariants.md (not my file to change).
- Limit: PIT's default mutators do not remove `lock.lock()`/`unlock()` calls nor the `atomically` wrapper meaningfully, and the test is single-threaded, so removing the lock would not be detected. The atomicity of check-and-save is built but unproven by any test (known gap from the plan; simultaneous booking outcome stays open).

## Behaviors added

- `BookSlot.book` on an unknown slot id throws `NoSuchElementException` (`orElseThrow()`): unspecified, untested; story 2 criterion 1 replaces it with `Refused(UNKNOWN_SLOT)`. Consumer-visible only if called with an unknown id; the plan states story 1 must not be released alone. Not a question for now (the plan already documents it).
- `null` identifiers: records accept them (D-22); `new Slot(null, ...)` etc. unvalidated.
- `Booking` is identified by patient and slot (no id), `BookingOutcome` is a sealed interface with nested records `Booked`/`Refused` (as the plan).
- `BookingStore` has `save(Booking)` besides the three methods in the plan's step 4 (the plan mentions "plus `save`"). `InMemoryBookingStore.findSlot` is read without the lock (slots are immutable after construction).
- Nothing else public.

## Deviations from the plan

None. Mutation was run with `--scope critical` (as requested), not `diff`.

## Blocking questions

None.
