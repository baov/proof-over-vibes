---
feature: book-a-slot
type: functional
priority: high
source: PRD req 10; story 2 criterion 6
automated_test: src/test/java/io/example/medical/BookSlotTest.java::overlapMeansSharingAStretchOfTime
status: covered
---

# Overlap means sharing a stretch of time, whatever the shape

- Given: a patient holds a slot
- When: the patient tries to book a slot that starts inside it, ends inside it, contains it, is contained in it, has the same range, or shares only one nanosecond with it
- Then: each booking is refused as overlapping
