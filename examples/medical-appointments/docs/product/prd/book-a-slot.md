# PRD: book a slot

Covers backlog items F2.1 (book a free slot) and F2.2 (refuse a slot already taken), picked together by the human. Status: ready. Product rules decided by the human; two boundary conventions are stated in section 5 for confirmation.

## 1. Problem

A patient who can see a practitioner's free slots must be able to secure one, and the service must never promise the same slot to two patients. Double-booking is the first anti-goal of `vision.md`; the cost of a lost or doubled slot is the capacity loss described in `research.md`, section 1.

## 2. Goal and success

Outcomes from the vision: a booking is completed without help, and no slot is ever booked by two patients. Measure: for every slot, at most one active booking exists; a booking of a free slot succeeds.

## 3. Users and use

A patient books a slot of a practitioner. Main path: the patient chooses a free slot, books it, and the slot is no longer free. If the slot is already taken, the booking is refused and the existing booking is unchanged.

## 4. Scope

**In.** Pure domain behavior: what a slot is, what a booking is, booking a free slot, refusing a taken one.
- A **slot** belongs to one practitioner, has a start and an end, and is either free or booked. Slots are already available (preloaded); how they get there is out of scope (F4.1).
- A **booking** links one patient to one slot.

**Out.** User interface, patient accounts and authentication, payment, cancellation (F3.1), listing free slots (F1.1), reminders, rescheduling, the design of the slot preload, anything about how the product is built.

## 5. Requirements

Each is observable from outside.

1. Booking a free slot succeeds and creates a booking for that patient on that slot.
2. After a successful booking, the slot is no longer free.
3. Booking a slot that is already booked is refused.
4. A refused booking changes nothing: the existing booking stays, and the slot keeps its patient.
5. A slot never has more than one active booking.
6. Booking a slot that does not exist is refused.
7. Booking a slot in the past is refused. A slot is in the past when its start is earlier than the current moment; a slot starting exactly now can still be booked. (The current moment is an input of the rule.)
8. A patient may hold several bookings, with one or several practitioners.
9. A booking is refused if its slot overlaps in time a slot the same patient already holds, whatever the practitioner.
10. Overlap: two slots overlap when each starts before the other ends, that is, they share a stretch of time longer than zero. Back-to-back slots (one ends exactly when the next starts) do not overlap.
11. A patient booking a slot they already hold is refused, like any taken slot.
12. Every refusal (taken, past, unknown, overlapping) changes nothing.

## 6. Risks and open questions

**Decided by the human:** past slots refused; several bookings per patient but no overlap; rebooking an own slot refused.

**To confirm (does not block).** The sources do not say whether back-to-back slots (requirement 10) and a slot starting exactly now (requirement 7) are allowed. Conventions chosen: both allowed. Tell me if not.

**Open, deliberately NOT decided here (reserved for later edge-case requests).**
- Two patients booking the same slot at the same moment: what the outcome must be. For the architect to take up as a technical unknown.
- Empty or blank patient or slot identifiers.

Other technical unknowns, for the architect: sensitive data (the booking links a person to a health practitioner: GDPR Article 9 context, *unverified*; see roadmap E5).

The human then creates the request citing this PRD.
