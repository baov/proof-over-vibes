---
feature: connection-requests
type: functional
priority: high
source: PRD R5
automated_test: tests/connections/pair-state.test.ts::is not connected with request state pending while a request is pending, seen from both members
status: covered
---

# State of a pair with a pending request

- Given: A->B pending
- When: the state is asked from either member
- Then: not connected, request state pending
