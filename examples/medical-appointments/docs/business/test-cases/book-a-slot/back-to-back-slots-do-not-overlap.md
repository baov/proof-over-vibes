---
feature: book-a-slot
type: functional
priority: high
source: PRD req 10, D-20; story 2 criterion 7
automated_test: src/test/java/io/example/medical/BookSlotTest.java::backToBackSlotsDoNotOverlap
status: covered
---

# Back to back slots do not overlap

- Given: a patient holds a slot
- When: the patient books a slot starting exactly when it ends, and a slot ending exactly when it starts
- Then: both bookings are made
