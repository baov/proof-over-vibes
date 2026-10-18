---
feature: book-a-slot
type: functional
priority: high
source: PRD req 3; story 1 criterion 3
automated_test: src/test/java/io/example/medical/BookSlotTest.java::refusesASlotBookedByAnotherPatient
status: covered
---

# A slot booked by someone else is refused as taken

- Given: a slot already booked by patient A
- When: patient B tries to book the same slot
- Then: the booking is refused, the reason being that the slot is taken
