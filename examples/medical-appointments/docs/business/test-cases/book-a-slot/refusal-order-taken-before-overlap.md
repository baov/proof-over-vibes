---
feature: book-a-slot
type: functional
priority: high
source: D-21, PRD req 11; story 2 criteria 9, 10
automated_test: src/test/java/io/example/medical/BookSlotTest.java::reportsTakenBeforeOverlap
status: covered
---

# A taken slot is reported as taken before overlapping

- Given: a patient holds a slot, and a slot taken by another patient overlaps it
- When: the patient tries to book the taken slot, and then the slot they already hold
- Then: each booking is refused as taken, not as overlapping
