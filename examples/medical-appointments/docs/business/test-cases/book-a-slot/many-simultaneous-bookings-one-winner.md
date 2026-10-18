---
feature: book-a-slot
type: functional
priority: medium
source: PRD edge-simultaneous scope; D-31, D-32
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::manySimultaneousBookingsLeaveOneWinnerAndTheRestRefusedForTheSameReason
status: covered
---

# With more than two simultaneous requests, one wins and all the others get the same refusal

- Given: a free slot wanted by five patients, and separately three free slots that overlap each other wanted by one patient
- When: all the requests arrive at the same moment
- Then: for the slot, one patient is booked and the four others are refused as taken; for the three slots, one is booked and the two others are refused as overlapping, and the patient holds one slot
