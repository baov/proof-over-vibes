---
feature: connection-requests
type: functional
priority: high
source: PRD R5
automated_test: tests/connections/pair-state.test.ts::is not connected with request state declined after a decline, seen from both members
status: covered
---

# State reports declined

- Given: A->B pending
- When: B declines it
- Then: the pair is not connected, request state declined, from both members
