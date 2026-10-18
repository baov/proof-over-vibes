---
feature: book-a-slot
type: functional
priority: high
source: PRD edge-blank-ids req 2, 3, 4; D-30, D-33
automated_test: src/test/java/io/example/medical/BookSlotTest.java::refusesASlotIdentifierThatIsAbsentEmptyOrBlank
status: covered
---

# A booking without a slot identifier is refused

- Given: a patient and a store that cannot be asked about a missing identifier
- When: a request names no slot, an empty slot, or a slot made only of white space, once or twice
- Then: the booking is refused each time, the reason being that an identifier is missing, and the patient holds nothing
