# PRD: book a slot, edge case: simultaneous bookings

Edge case of `book-a-slot.md` (open point "two patients booking the same slot at the same moment"). Status: ready.

## 1. Problem

Two requests can arrive at the same moment. The service already guarantees that at most one booking succeeds (requirement 5 of `book-a-slot.md`); what the other request must be told has never been decided.

## 2. Goal and success

No double-booking, no overlapping bookings for one patient, and a loser who gets a clear and consistent answer. Measure: whatever the arrival timing, the outcome is one that could have happened if the requests had come one after the other.

## 3. Users and use

Case A: two patients book the same free slot at the same moment. Case B: one patient books two overlapping slots at the same moment. In each case one booking succeeds and the other request is refused.

## 4. Scope

**In.** The outcome seen by the request that does not succeed, in cases A and B; which request wins.

**Out.** Performance and fairness guarantees; more than two concurrent requests beyond applying the same rule; retries by the caller; how the exclusion is built.

## 5. Requirements

1. In case A exactly one booking is created; the slot has one patient.
2. In case A the other request is refused with TAKEN, as if it had arrived just after the winner.
3. In case B exactly one of the two bookings is created; the patient holds no overlapping slots.
4. In case B the other request is refused with OVERLAPPING, as if it had arrived just after the winner.
5. The refusal reason is the one the existing order (D-21) gives after the winner's booking: for example, if the slot is also past, PAST still comes before TAKEN.
6. Which of the two requests wins is not guaranteed.
7. The refusal changes nothing; the winner's booking is unchanged.

## 6. Risks and open questions

Decisions:
- Same-slot loser sees TAKEN, **human**.
- Overlapping-slots loser sees OVERLAPPING, **human**.
- Either request may win, no ordering promised, **delegated** (recommendation of the Product Manager, relayed by the orchestrator, nobody read it; cheap to reverse).

Technical unknown, for the architect: the existing lock already keeps the "at most one" rule; making the loser's reason match requirements 2 and 4 is a question for the plan.
