---
feature: book-a-slot
type: functional
priority: high
source: PRD req 11, D-11; story 1 criterion 4
automated_test: src/test/java/io/example/medical/BookSlotTest.java::refusesASlotThePatientAlreadyHolds
status: covered
---

# A patient booking again a slot they already hold is refused as taken

- Given: a slot already booked by patient A
- When: patient A books the same slot again
- Then: the booking is refused, the reason being that the slot is taken
