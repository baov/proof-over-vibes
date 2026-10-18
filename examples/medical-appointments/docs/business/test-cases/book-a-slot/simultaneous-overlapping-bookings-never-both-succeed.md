---
feature: book-a-slot
type: functional
priority: high
source: PRD req 5, 9 only
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::twoSimultaneousOverlappingBookingsByOnePatientNeverBothSucceed
status: covered
---

# Two simultaneous bookings of overlapping slots never both succeed

- Given: two free slots that overlap in time
- When: one patient tries to book both at the same moment
- Then: at most one booking is made, and the patient holds at most one of the two slots

What is shown for the other attempt is not specified yet.
