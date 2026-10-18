---
feature: connection-requests
type: functional
priority: high
source: PRD R1, D-26
automated_test: tests/connections/blank-member-id.test.ts::rejects the erasure of a blank member and erases nothing
status: covered
---

# Erasing a blank member id is rejected and erases nothing

- Given: A->B pending
- When: a blank member is erased, twice
- Then: blank-member-id both times, the request is still pending; erasing a non-blank unknown member still succeeds
