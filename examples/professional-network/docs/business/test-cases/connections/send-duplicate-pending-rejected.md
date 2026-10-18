---
feature: connection-requests
type: functional
priority: high
source: PRD R9
automated_test: tests/connections/send-request.test.ts::rejects a second request to the same member while one is pending
status: covered
---

# A duplicate pending request is rejected

- Given: A->B pending
- When: A sends to B again
- Then: rejected with the duplicate-pending reason; the pending list still holds one request
