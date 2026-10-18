---
feature: connection-requests
type: functional
priority: high
source: PRD R14, D-7
automated_test: tests/connections/send-request.test.ts::rejects a new request from the member whose request was declined, and stores nothing
status: covered
---

# After a decline, a new request from the same sender is rejected

- Given: A->B declined
- When: A sends to B again
- Then: it is rejected as previously-declined, nothing is stored and the state is still declined
