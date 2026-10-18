---
feature: book-a-slot
type: functional
priority: high
source: PRD req 8, D-10; story 2 criterion 4
automated_test: src/test/java/io/example/medical/BookSlotTest.java::aPatientHoldsSeveralSlotsThatDoNotOverlap
status: covered
---

# A patient can hold several slots that do not overlap

- Given: a patient holds one slot
- When: the patient books a second slot that does not overlap it, with the same practitioner and then with another practitioner
- Then: both bookings are made and the patient holds all three slots
