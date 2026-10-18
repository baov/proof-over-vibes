---
feature: book-a-slot
type: functional
priority: high
source: PRD edge-simultaneous req 7; book-a-slot req 12
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::aRefusedSimultaneousBookingLeavesNothingBehind
status: covered
---

# A request refused in a simultaneous booking changes nothing

- Given: two patients who raced for one slot, or one patient who raced for two overlapping slots
- When: the race is over
- Then: the winner's booking is the one the winner was told about; the other patient can book another free slot, and asking again for the lost slot gives the same refusal and changes nothing; the slot of the refused request is still free for someone else
