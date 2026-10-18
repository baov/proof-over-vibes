---
feature: book-a-slot
type: functional
priority: high
source: PRD req 7, D-19; story 2 criterion 3
automated_test: src/test/java/io/example/medical/BookSlotTest.java::booksASlotStartingExactlyNow
status: covered
---

# A slot starting exactly now can be booked

- Given: a slot that starts at this very moment, and another that starts an instant later
- When: a patient books each one
- Then: both bookings are made
