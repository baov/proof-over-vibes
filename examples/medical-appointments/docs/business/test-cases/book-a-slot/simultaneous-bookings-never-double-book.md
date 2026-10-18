---
feature: book-a-slot
type: functional
priority: high
source: PRD req 5 only
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::twoSimultaneousBookingsOfOneSlotNeverBothSucceed
status: covered
---

# Two simultaneous bookings never double-book a slot

- Given: a free slot
- When: two patients try to book it at the same moment
- Then: at most one booking is made, and the slot holds at most that one booking

What the other patient is shown is not specified yet.
