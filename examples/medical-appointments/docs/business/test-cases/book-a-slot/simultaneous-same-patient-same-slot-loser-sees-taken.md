---
feature: book-a-slot
type: functional
priority: medium
source: book-a-slot PRD req 11; D-11, D-21
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::aPatientBookingTheSameSlotTwiceAtOnceSeesTakenForTheOther
status: covered
---

# A patient asking twice at once for the same slot: the second is refused as taken

- Given: a free slot
- When: the same patient tries to book it twice at the same moment
- Then: one request is booked, the other is refused as taken (not as overlapping); the patient holds the slot once
