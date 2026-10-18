---
feature: book-a-slot
type: functional
priority: medium
source: PRD edge-blank-ids req 6
automated_test: src/test/java/io/example/medical/BookSlotTest.java::reportsOneRefusalWhenBothIdentifiersAreMissing
status: covered
---

# Both identifiers missing give a single refusal

- Given: a free slot in the future
- When: a request names neither a patient nor a slot, in any of the missing forms (nothing, empty, white space)
- Then: one refusal is returned, the reason being that an identifier is missing, and nothing is stored
