---
feature: book-a-slot
type: functional
priority: high
source: PRD req 1; story 1 criterion 1
automated_test: src/test/java/io/example/medical/BookSlotTest.java::booksAFreeSlotForThePatient
status: covered
---

# A patient books a free slot

- Given: a practitioner's slot with no booking
- When: the patient books it
- Then: the booking is confirmed for that patient on that slot, and the slot holds that booking
