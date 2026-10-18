---
feature: book-a-slot
type: functional
priority: high
source: PRD edge-blank-ids req 5; D-34 (extends D-21)
automated_test: src/test/java/io/example/medical/BookSlotTest.java::reportsAMissingIdentifierBeforeAnyOtherRefusal
status: covered
---

# A missing identifier is reported before any other reason

- Given: slots that are unknown, already started, held by another patient, or overlapping the patient's own, and a patient who holds slots
- When: a request names no patient (or no slot) while the slot is also unknown, started, taken or overlapping
- Then: the booking is refused as an identifier missing, never for the other reason, and nothing changes
