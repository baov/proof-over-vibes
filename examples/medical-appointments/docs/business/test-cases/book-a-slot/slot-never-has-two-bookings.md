---
feature: book-a-slot
type: functional
priority: high
source: PRD req 5; story 1 criterion 6
automated_test: src/test/java/io/example/medical/BookSlotTest.java::aSlotNeverHoldsMoreThanOneBookingWhateverTheSequence
status: covered
---

# A slot never holds two bookings, whatever the order of attempts

- Given: several slots and several patients, attempts mixing repeats, other patients and other slots, one after another
- When: all the attempts have been made
- Then: each slot holds at most one booking, and it is that of the first patient who succeeded on it
