---
feature: book-a-slot
type: functional
priority: high
source: D-21; story 2 criteria 9, 10
automated_test: src/test/java/io/example/medical/BookSlotTest.java::reportsUnknownBeforeAnyOtherRefusal
status: covered
---

# An unknown slot is reported before any other reason

- Given: a patient holds slots and the current moment is after all of them
- When: the patient tries to book a slot that does not exist
- Then: the booking is refused as unknown
