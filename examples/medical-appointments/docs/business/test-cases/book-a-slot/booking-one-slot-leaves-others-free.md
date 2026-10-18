---
feature: book-a-slot
type: functional
priority: medium
source: PRD req 1, 2, 5
automated_test: src/test/java/io/example/medical/BookSlotTest.java::bookingOneSlotLeavesOtherSlotsFree
status: covered
---

# Booking a slot does not affect other slots

- Given: two free slots, patient A books the first
- When: patient B books the second
- Then: both are booked, each by its own patient
