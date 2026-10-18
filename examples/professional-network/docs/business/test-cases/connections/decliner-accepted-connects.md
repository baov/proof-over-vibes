---
feature: connection-requests
type: functional
priority: high
source: PRD R7
automated_test: tests/connections/accept-request.test.ts::connects the two when the original sender accepts the decliner's request
status: covered
---

# Accepting the decliner's request connects the two

- Given: A->B declined, then B->A pending
- When: A accepts B->A
- Then: A and B are connected, the earlier request stays declined
