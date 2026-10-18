---
feature: connection-requests
type: functional
priority: high
source: PRD R3, R5
automated_test: tests/connections/pair-state.test.ts::is connected with request state accepted once the recipient accepts, seen from both members
status: covered
---

# The recipient accepts: the two are connected, each to the other

- Given: A->B pending
- When: B accepts
- Then: the state of the pair is connected with request state accepted, from either member
