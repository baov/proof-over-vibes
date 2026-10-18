---
feature: book-a-slot
type: functional
priority: medium
source: D-34; PRD edge-simultaneous req 5
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::aMissingIdentifierIsReportedAsMissingWhileSomeoneElseBooksTheSlot
status: covered
---

# A missing identifier is reported as missing while someone else books the slot

- Given: a free slot
- When: one patient books it while requests with a blank patient identifier and with no slot identifier arrive at the same moment; and, separately, two requests with a missing identifier arrive together
- Then: the patient is booked, every request with a missing identifier is refused as missing (never as taken), and the store holds nothing for them
