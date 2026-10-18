---
feature: book-a-slot
type: functional
priority: high
source: PRD req 6, D-26; story 2 criterion 1
automated_test: src/test/java/io/example/medical/BookSlotTest.java::refusesAnUnknownSlot
status: covered
---

# A slot that does not exist is refused as unknown

- Given: no slot with the requested identity exists
- When: a patient tries to book it, once or twice
- Then: the booking is refused each time, the reason being that the slot is unknown, and nothing is stored
