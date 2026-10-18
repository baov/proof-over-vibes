---
feature: book-a-slot
type: functional
priority: high
source: PRD req 12, 4; story 2 criterion 8
automated_test: src/test/java/io/example/medical/BookSlotTest.java::anUnhonourableRefusalChangesNothing
status: covered
---

# A refusal changes nothing

- Given: several slots, some already booked by different patients
- When: a patient is refused because the slot is unknown, already started, or overlaps one they hold
- Then: no booking is added, no slot changes hands, and every patient still holds the same slots
