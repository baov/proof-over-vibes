---
feature: book-a-slot
type: functional
priority: medium
source: PRD edge-blank-ids req 3; D-33, D-37
automated_test: src/test/java/io/example/medical/BookSlotTest.java::onlyWhiteSpaceMakesAnIdentifierBlank
status: covered
---

# Only white space makes an identifier blank

- Given: free slots, and identifiers that look empty but are not white space (a zero-width character, a control character) or that merely have spaces around a name
- When: patients with such identifiers book a free slot, and a patient books a slot whose identifier has spaces around it or is a zero-width character
- Then: the patients are booked as given, and the two slot identifiers are refused as unknown slots
