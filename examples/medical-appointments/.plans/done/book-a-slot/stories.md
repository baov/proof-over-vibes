---
role: product-owner
status: done
reasons: []
---

# Stories: book a slot

Feature: F2.1 + F2.2 (D-8), PRD `docs/product/prd/book-a-slot.md`. Two stories, thinnest path first. Sources: PRD requirement numbers ("req n") and decision ids from `docs/business/decisions.md`. No glossary exists yet.

## Story 1: Book a free slot, and never double-book it

*As a patient, I want to book a free slot of a practitioner, so that I secure it and nobody else can take it.*

Value: closes the journey end to end on the happy path and holds the first anti-goal (no double-booking). Everything is observable from outside the domain.

Acceptance criteria:
1. Booking a free slot succeeds and creates a booking linking that patient to that slot. (req 1)
2. After that booking, the slot is no longer free. (req 2)
3. Booking a slot that is already booked by another patient is refused. (req 3)
4. Booking a slot the same patient already holds is refused, like any taken slot. (req 11, D-11)
5. After a refusal for a taken slot, the existing booking is unchanged and the slot keeps its patient. (req 4, req 12)
6. A slot never has more than one active booking, whatever the sequence of sequential attempts. (req 5)

## Story 2: Refuse a booking that cannot be honoured

*As a patient, I want a booking to be refused clearly when the slot is unknown, past, or clashes with one of my own, so that I never hold a booking that cannot happen.*

Value: completes the refusal rules; the patient may hold several bookings, as long as they do not collide. Depends on story 1.

Acceptance criteria:
1. Booking a slot that does not exist is refused. (req 6)
2. Booking a slot whose start is earlier than the current moment is refused; the current moment is an input of the rule. (req 7, D-9)
3. Booking a slot that starts exactly at the current moment succeeds. (req 7, D-19: stated by the Product Manager, not read by a person)
4. A patient may hold several bookings, with one or several practitioners, as long as the slots do not overlap. (req 8, D-10)
5. A booking is refused if its slot overlaps in time a slot the same patient already holds, whatever the practitioner. (req 9, D-10)
6. Two slots overlap when each starts before the other ends, that is, they share a stretch of time longer than zero. (req 10)
7. Back-to-back slots (one ends exactly when the next starts) do not overlap, so both can be held. (req 10, D-20: stated by the Product Manager, not read by a person)
8. After a refusal for an unknown, past or overlapping slot, nothing changes: no booking is created, no slot changes state, existing bookings are unchanged. (req 12, req 4)
9. When a booking breaks several rules at once, the refusal reported is the first in this single order: unknown slot, then past, then taken (including a slot the patient already holds), then overlap with another slot the patient holds. (D-21)
10. Pairs that can co-occur follow that order: unknown with any other rule is reported unknown; past and taken is reported past; past and overlap is reported past; taken and overlap is reported taken (a slot the patient holds also overlaps itself: reported taken, as req 11 asks). (D-21)
11. A slot's time range is valid only if its end is strictly after its start; a zero-length, inverted or absent range is rejected at creation, so every slot considered by the overlap rule has a positive length. (D-27)
12. Two overlapping slots of the same practitioner may be booked by two different patients: the overlap rule applies per patient only. (D-28, req 9)

## Open points

Both PRD questions stay open and undecided (PRD section 6); no criterion above depends on them.

1. **Simultaneous booking of one slot by two patients: what outcome must be guaranteed?** Options: (a) exactly one succeeds and the other is refused like a taken slot; (b) another outcome the human defines. Source: PRD section 6, backlog note on concurrency (a technical unknown for the architect). Story 1 criterion 6 covers sequential attempts only.
2. **Empty or blank patient or slot identifiers: what happens?** Options: (a) refused like an unknown slot or patient; (b) refused with a distinct reason; (c) accepted. Source: PRD section 6.

Precedence of refusals is no longer open: see D-21 and story 2 criteria 9-10.
