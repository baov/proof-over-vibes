---
feature: book-a-slot
type: functional
priority: high
source: PRD edge-blank-ids req 1, 3, 4; D-30, D-33
automated_test: src/test/java/io/example/medical/BookSlotTest.java::refusesAPatientIdentifierThatIsAbsentEmptyOrBlank
status: covered
---

# A booking without a patient identifier is refused

- Given: a free slot in the future
- When: a request names no patient, an empty patient, or a patient made only of white space (spaces, a tab, a line break, a non-breaking space), once or twice
- Then: the booking is refused each time, the reason being that an identifier is missing, and the slot stays free
