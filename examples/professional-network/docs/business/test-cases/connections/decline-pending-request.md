---
feature: connection-requests
type: functional
priority: high
source: PRD R4
automated_test: tests/connections/decline-request.test.ts::the recipient declines a pending request: not connected, state declined, no longer pending
status: covered
---

# The recipient declines a pending request; not connected, state declined

- Given: A->B and C->B pending
- When: B declines A->B
- Then: the request is declined, A and B are not connected, the state is declined from both sides and only C->B remains in B's pending list
