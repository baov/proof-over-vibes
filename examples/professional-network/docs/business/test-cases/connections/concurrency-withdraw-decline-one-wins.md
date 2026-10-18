---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/concurrency.test.ts::lets exactly one of withdraw and decline succeed on the same request
status: covered
---

# Withdraw and decline at once: one wins

- Given: A->B pending
- When: A withdraws and B declines the request at the same moment
- Then: exactly one succeeds and the other is rejected as not-pending; the final state is the winner's and the pair is not connected
