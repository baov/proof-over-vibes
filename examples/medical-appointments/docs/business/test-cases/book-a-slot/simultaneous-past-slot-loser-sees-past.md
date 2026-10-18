---
feature: book-a-slot
type: functional
priority: high
source: PRD edge-simultaneous req 5; D-21
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::aLoserJudgedAfterTheSlotHasStartedSeesPastNotTakenOrOverlapping
status: covered
---

# A request judged after the slot has started is refused as past, not as taken or overlapping

- Given: a slot that starts shortly, wanted by two patients (or two overlapping slots wanted by one patient), and the moment judged for the second request is after the start
- When: the requests arrive at the same moment
- Then: the first one judged is booked, the other is refused as past
