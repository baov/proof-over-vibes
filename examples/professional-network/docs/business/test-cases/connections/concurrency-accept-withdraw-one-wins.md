---
feature: connection-requests
type: functional
priority: high
source: PRD R3, R4
automated_test: tests/connections/concurrency.test.ts::lets exactly one of accept and withdraw succeed on the same request, and the state matches the winner
status: covered
---

# Accept and withdraw at once: one wins

- Given: A->B pending
- When: B accepts and A withdraws the request at the same moment
- Then: exactly one succeeds and the other is rejected as not-pending; if the accept won, the pair is connected and the request accepted, otherwise it is withdrawn and the pair not connected; never connected with a withdrawn request
