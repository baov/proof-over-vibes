---
feature: connection-requests
type: functional
priority: high
source: PRD R9 (per pair)
automated_test: tests/connections/send-request.test.ts::still allows a request to another member while one is pending
status: covered
---

# A request to a third member stays allowed

- Given: A->B pending
- When: A sends to C
- Then: the request is accepted
