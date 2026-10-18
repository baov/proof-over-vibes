---
feature: book-a-slot
type: functional
priority: high
source: D-21; story 2 criteria 9, 10
automated_test: src/test/java/io/example/medical/BookSlotTest.java::reportsPastBeforeTakenAndOverlap
status: covered
---

# A past slot is reported as past before taken or overlapping

- Given: slots that have started, one taken by another patient and overlapping one the patient holds, one only taken, one only overlapping
- When: the patient tries to book each of them
- Then: each booking is refused as past
