---
feature: book-a-slot
type: functional
priority: high
source: PRD req 2; story 1 criterion 2
automated_test: src/test/java/io/example/medical/BookSlotTest.java::slotIsNoLongerFreeAfterBooking
status: covered
---

# A booked slot is no longer free

- Given: a free slot, then a patient books it
- When: the slot is looked at again
- Then: the slot holds an active booking: it is no longer free
