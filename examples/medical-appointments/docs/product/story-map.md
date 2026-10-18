# Story map

Backbone, left to right. Features under each step, most essential first. Status is `idea` for all: no code exists.

| Set up availability | See free slots | Book | Cancel |
|---|---|---|---|
| E4: F4.1 Preloaded availability (skeleton) | E1: F1.1 List a practitioner's free slots | E2: F2.1 Book a free slot | E3: F3.1 Cancel a booking |
| E4: F4.2 Practitioner defines availability | E1: F1.2 Free slots of a chosen day | E2: F2.2 Refuse a taken slot (no double-booking) | E3: F3.2 Cancelled slot is bookable again |
| | | | |
| Later / Next | E5: F5.1 Minimal data collected | E6: F6.1 Reminder before visit | E7: F7.1 Reschedule |

## Slices

- **Slice 1, walking skeleton**: F4.1, F1.1, F2.1, F2.2, F3.1, F3.2. One practitioner, preloaded availability: see, book, cancel, end to end.
- **Slice 2**: F4.2, F1.2. Practitioner-managed availability, browse by day.
- **Slice 3 (Next)**: F5.1 and further E5 features, F6.1.
- **Slice 4 (Later)**: F7.1.
