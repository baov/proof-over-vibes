---
feature: connection-requests
type: functional
priority: high
source: PRD R15, D-8
automated_test: tests/connections/accept-request.test.ts::rejects accepting a request that is already accepted, and nothing changes
status: covered
---

# Accept on an accepted request is rejected

- Given: A->B accepted
- When: B accepts again
- Then: rejected with the not-pending reason
