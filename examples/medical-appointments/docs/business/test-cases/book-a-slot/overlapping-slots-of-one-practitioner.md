---
feature: book-a-slot
type: functional
priority: medium
source: D-28; story 2 criterion 12
automated_test: src/test/java/io/example/medical/BookSlotTest.java::overlappingSlotsOfOnePractitionerCanBeBookedByDifferentPatients
status: covered
---

# Overlapping slots of one practitioner can go to different patients

- Given: two overlapping slots of the same practitioner
- When: one patient books the first and another patient books the second
- Then: both bookings are made; the overlap rule applies per patient
