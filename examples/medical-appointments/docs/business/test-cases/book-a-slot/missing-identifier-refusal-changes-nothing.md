---
feature: book-a-slot
type: functional
priority: high
source: PRD edge-blank-ids req 7; req 12 of book-a-slot
automated_test: src/test/java/io/example/medical/BookSlotTest.java::aMissingIdentifierRefusalChangesNothing
status: covered
---

# A refusal for a missing identifier changes nothing

- Given: bookings already held and free slots
- When: requests with a missing patient or slot are refused
- Then: every slot keeps its booking or stays free, and later valid bookings of those slots still succeed
