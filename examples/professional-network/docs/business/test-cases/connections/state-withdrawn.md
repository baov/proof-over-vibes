---
feature: connection-requests
type: functional
priority: high
source: PRD R5
automated_test: tests/connections/pair-state.test.ts::is not connected with request state withdrawn after a withdrawal, seen from both members
status: covered
---

# State reports withdrawn

- Given: A->B pending
- When: A withdraws it
- Then: the pair is not connected, request state withdrawn, from both members
