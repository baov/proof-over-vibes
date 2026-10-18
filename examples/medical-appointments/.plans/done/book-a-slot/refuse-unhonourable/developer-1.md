---
role: developer
status: done
reasons: []
---

# Developer note, iteration 1: story 2 (refuse-unhonourable)

Skills announced: `plan-driven-dev` (implementation steps), `behavior-driven-testing`. The plan was followed with no deviation.

## Commits (on the shared branch, only files under examples/medical-appointments)

1. `13ec422` Add the TimeRange value object, valid by construction (D-27, D-29)
2. `1874c1d` Give slots a time range and BookSlot a clock; pin the exact booking after booking (steps 2, 5 partly, 7; comment on `findSlot`)
3. `e02120e` Refuse an unknown slot instead of throwing (D-26) (closes M2)
4. `ac71d76` Refuse a slot that started before now; a slot starting exactly now is bookable (D-19)
5. `8646c69` Refuse a slot overlapping one the patient holds; back to back slots are fine (D-20, D-28) (port `slotsHeldBy`)
6. `37786c1` Pin the order of refusals and that a refusal changes nothing (D-21)
7. `b900bcb` Prove check-and-save is atomic under simultaneous bookings, without deciding what the loser sees (closes M1)

15 business test-cases added under `docs/business/test-cases/book-a-slot/`, as listed in the plan.

## Results

- `bash tools/harness/run_all.sh --with-mutation`: exit 0. INV-001 green; INV-002: 22 test-cases, 22 covered_ok, 0 broken, 0 orphan tests; INV-003 (scope critical, PIT): **100.0%, 18 killed / 18 generated, no survivor**. No threshold or baseline written (human decision). 22 tests green, repeated 3 times with no flakiness.
- Red observed for: unknown slot (NoSuchElementException), past/now (test failed on the old rule), overlap (checked by neutralizing the overlap condition: 2 tests failed, then restored). The tests of the order, the snapshot and `TimeRange` were written after, or together with, the code that already satisfied them (characterization of the rule): their value was checked through the mutation run, not by a separate red.

## M1: does removing the lock make the tests fail?

Yes. With `atomically` reduced to `unit.get()` locally, both `BookSlotConcurrencyTest` tests fail (both bookings succeed: "both bookings of the same slot succeeded", "a patient booked two overlapping slots"). Lock restored; the experiment is in no commit (the adapter is identical to HEAD). The tests do not look at the loser's outcome. The decorator makes the interleaving deterministic; each concurrency test takes about 0.5 s because, with the lock, the wait times out by design.

Caveat: the lock lives in `adapters`, outside the PIT scope, so mutation still does not cover it; the tests above do.

## Behaviors added

None beyond the plan. Public surface that changed, all stated by the plan: `Slot(id, practitioner, range)`; `TimeRange` (rejects invalid ranges with `IllegalArgumentException`, D-27/D-29); `BookSlot(store, clock)`; port `BookingStore.slotsHeldBy(PatientId)`; `BookingRule.decide(patient, Optional<Slot>, now, activeBooking, heldSlots)`. A `null` clock, null identifiers: unspecified (D-22), untested.

## Technical points for the reviewer

- `slotsHeldBy` scans the bookings under the lock (a real database would index by patient).
- The clock is read once per attempt, inside the atomic unit.
- `findSlot` reads without the lock; a comment says why (slots are fixed at construction).
- `slotIsNoLongerFreeAfterBooking` now asserts the exact booking.
- Minor from story 1 not touched: no mutation baseline (human decision).

## Questions

None.
