---
feature: book-a-slot
type: functional
priority: medium
source: D-27, D-29; story 2 criterion 11
automated_test: src/test/java/io/example/medical/TimeRangeTest.java::aRangeEndingNotAfterItsStartIsRejected
status: covered
---

# A slot's time range must end after it starts

- Given: a start and an end for a slot
- When: the end is after the start, even by the smallest amount
- Then: the time range exists
- When: the end is the same as the start, before it, or either one is missing
- Then: the time range is rejected when the slot is created
