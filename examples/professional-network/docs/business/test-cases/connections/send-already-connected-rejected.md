---
feature: connection-requests
type: functional
priority: high
source: PRD R11, D-6
automated_test: tests/connections/send-request.test.ts::rejects a request between two connected members, whichever of them sends it
status: covered
---

# A request between connected members is rejected, both directions

- Given: A and B connected
- When: A sends to B, then B sends to A
- Then: both rejected with the already-connected reason, nothing pending
