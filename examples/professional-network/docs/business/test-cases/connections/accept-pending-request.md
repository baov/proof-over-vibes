---
feature: connection-requests
type: functional
priority: high
source: PRD R3
automated_test: tests/connections/accept-request.test.ts::the recipient accepts a pending request and it is no longer pending
status: covered
---

# The recipient accepts a pending request, it leaves their pending list

- Given: A->B and C->B pending
- When: B accepts A->B
- Then: the request is accepted and only C->B remains in B's pending list
