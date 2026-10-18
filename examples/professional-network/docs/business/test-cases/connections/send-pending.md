---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/send-request.test.ts::a member sends a request to another member and it is pending
status: covered
---

# A member sends a request, it is pending

- Given: two distinct members with no request
- When: the first sends a request to the second
- Then: a request exists in state pending, with the first as sender and the second as recipient
