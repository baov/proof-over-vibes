# Backlog

Priority order. Method: MoSCoW, validated by the human; the cut is per slice and Won't means "not in this horizon". No user stories: they come with the PRD of a picked feature. Statuses are `idea` except F2.1 and F2.2, `picked` together as the feature "book a slot" (PRD: `prd/book-a-slot.md`).

## Slice 1 (Now): walking skeleton

| # | Item | Epic / outcome | Value | MoSCoW | Status |
|---|---|---|---|---|---|
| 1 | F1.1 List a practitioner's free slots | E1 / easy booking | The patient knows when the practitioner is free. | Must | idea |
| 2 | F2.1 Book a free slot | E2 / easy booking | The patient secures a slot. | Must | picked |
| 3 | F2.2 Refuse a slot already taken | E2 / no double-booking | A slot never goes to two patients. | Must | picked |
| 4 | F3.1 Cancel a booking | E3 / slot reuse | The patient can undo a booking. | Must | idea |
| 5 | F3.2 Cancelled slot is bookable again | E3 / slot reuse | A cancellation does not waste capacity. | Must | idea |
| 6 | F4.1 Preloaded availability | E4 / slots exist | Slots exist to test the three verbs. | Must | idea |

Why: the idea names exactly three verbs; the skeleton is the thinnest path that proves them, and double-booking is the first anti-goal.

## Slice 2 (Now)

| # | Item | Epic / outcome | Value | MoSCoW | Status |
|---|---|---|---|---|---|
| 7 | F4.2 Practitioner defines availability | E4 / slots exist | Real slots without a developer. | Should | idea |
| 8 | F1.2 Free slots of a chosen day | E1 / easy booking | Faster to find a convenient slot. | Could | idea |

## Next

| # | Item | Epic / outcome | Value | MoSCoW | Status |
|---|---|---|---|---|---|
| 9 | F5.1 Minimal data collected | E5 / anti-goal on data | Only what the booking needs is collected. | Should | idea |
| 10 | F6.1 Reminder before visit | E6 / fewer lost slots | Fewer forgotten visits. | Could | idea |

## Later

| # | Item | Epic / outcome | Value | MoSCoW | Status |
|---|---|---|---|---|---|
| 11 | F7.1 Reschedule a booking | E7 / easy booking | One step instead of cancel then book. | Won't (for now) | idea |

Open question for a later PRD, for the architect: how concurrent bookings of one slot are made safe (technical, not decided here).
