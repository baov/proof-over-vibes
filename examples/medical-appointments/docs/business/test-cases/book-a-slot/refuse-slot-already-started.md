---
feature: book-a-slot
type: functional
priority: high
source: PRD req 7, D-9; story 2 criterion 2
automated_test: src/test/java/io/example/medical/BookSlotTest.java::refusesASlotStartingBeforeNow
status: covered
---

# A slot that has already started is refused as past

- Given: a slot that started a moment ago, and another that started hours ago
- When: a patient tries to book either one
- Then: the booking is refused, the reason being that the slot is in the past, and nothing is stored
