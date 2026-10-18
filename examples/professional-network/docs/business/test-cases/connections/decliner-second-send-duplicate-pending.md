---
feature: connection-requests
type: functional
priority: high
source: PRD R9
automated_test: tests/connections/send-request.test.ts::rejects a second request of the decliner while the first is pending
status: covered
---

# The decliner cannot send twice while the first request is pending

- Given: A->B declined, then B->A pending
- When: B sends to A again
- Then: it is rejected as duplicate-pending
