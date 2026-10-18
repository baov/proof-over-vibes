---
feature: book-a-slot
type: functional
priority: high
source: PRD edge-simultaneous section 2
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::aSimultaneousOutcomeIsOneThatSomeOrderOneAfterTheOtherWouldGive
status: covered
---

# Whatever the timing, the result is one the same requests would give one after the other

- Given: requests that conflict in several ways (one patient asking for two overlapping slots while another asks for the second; a chain of slots where only neighbours overlap; a patient who already holds a slot overlapping the contested one)
- When: the requests arrive at the same moment
- Then: what each request is told, and the bookings left, are exactly those of some order in which the requests could have come one after the other
