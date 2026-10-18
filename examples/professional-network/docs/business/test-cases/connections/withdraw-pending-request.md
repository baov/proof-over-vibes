---
feature: connection-requests
type: functional
priority: high
source: PRD R12
automated_test: tests/connections/withdraw-request.test.ts::the sender withdraws a pending request: not connected, state withdrawn, no longer pending
status: covered
---

# The sender withdraws a pending request; state withdrawn

- Given: A->B pending
- When: A withdraws it
- Then: the request is withdrawn, A and B are not connected, the state is withdrawn and B's pending list is empty
