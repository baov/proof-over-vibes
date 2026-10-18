---
feature: book-a-slot
type: functional
priority: high
source: PRD edge-simultaneous req 3, 4, 7; D-32
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::oneOfTwoSimultaneousOverlappingBookingsOfAPatientWinsAndTheOtherSeesOverlapping
status: covered
---

# Two simultaneous bookings of overlapping slots: one wins, the other is refused as overlapping

- Given: two free slots that overlap in time
- When: one patient tries to book both at the same moment
- Then: one of the two is booked (either may be the one), the other is refused as overlapping; the patient holds the booked slot only, and the other slot stays free
