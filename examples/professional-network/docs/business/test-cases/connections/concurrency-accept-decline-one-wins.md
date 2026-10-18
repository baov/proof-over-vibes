---
feature: connection-requests
type: functional
priority: high
source: PRD R5
automated_test: tests/connections/concurrency.test.ts::lets exactly one of accept and decline succeed on the same request, the other is not-pending
status: covered
---

# Accept and decline at once: one wins

- Given: A->B pending
- When: B accepts and B declines the request at the same moment
- Then: exactly one succeeds and the other is rejected as not-pending; the final state (connected and accepted, or declined and not connected) is the winner's
