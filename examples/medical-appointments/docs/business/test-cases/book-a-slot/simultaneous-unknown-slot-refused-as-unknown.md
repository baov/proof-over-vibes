---
feature: book-a-slot
type: functional
priority: medium
source: D-21
automated_test: src/test/java/io/example/medical/BookSlotConcurrencyTest.java::simultaneousBookingsOfAnUnknownSlotAreAllRefusedAsUnknown
status: covered
---

# Simultaneous bookings of an unknown slot are all refused as unknown

- Given: a slot that does not exist, and a free slot that does
- When: two patients try to book the unknown slot while a third books the free one, all at the same moment
- Then: the two requests on the unknown slot are refused as unknown (never as taken), the third patient is booked, and nothing is stored for the unknown slot
