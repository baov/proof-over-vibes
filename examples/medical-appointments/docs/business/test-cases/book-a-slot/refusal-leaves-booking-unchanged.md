---
feature: book-a-slot
type: functional
priority: high
source: PRD req 4, 12; story 1 criterion 5
automated_test: src/test/java/io/example/medical/BookSlotTest.java::aTakenRefusalLeavesTheExistingBookingUnchanged
status: covered
---

# A refusal changes nothing

- Given: a slot booked by patient A, then a refused attempt by patient B and a repeated attempt by A
- When: the slot is looked at again
- Then: the booking on the slot is still A's, unchanged
