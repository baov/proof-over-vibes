---
feature: book-a-slot
type: functional
priority: high
source: PRD req 9, D-10; story 2 criterion 5
automated_test: src/test/java/io/example/medical/BookSlotTest.java::refusesASlotOverlappingOneThePatientHolds
status: covered
---

# A slot overlapping one the patient holds is refused

- Given: a patient holds a slot of one practitioner, and another slot of a different practitioner overlaps it
- When: the same patient tries to book the second slot, whichever slot was booked first
- Then: the booking is refused, the reason being the overlap, and the patient still holds only the first slot; another patient can book the second slot
