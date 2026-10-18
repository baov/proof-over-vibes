---
feature: book-a-slot
type: functional
priority: high
source: PRD edge-simultaneous req 1, 2, 7; D-31
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::oneOfTwoSimultaneousBookingsOfASlotWinsAndTheOtherSeesTaken
status: covered
---

# Two simultaneous bookings of one slot: one wins, the other is refused as taken

- Given: a free slot
- When: two patients try to book it at the same moment
- Then: one of them is booked (either may be the one), the other is refused as taken; the slot holds the winner's booking only, and the other patient holds nothing
