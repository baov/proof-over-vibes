---
feature: connection-requests
type: functional
priority: high
source: PRD R2
automated_test: tests/connections/accept-request.test.ts::rejects the sender accepting their own request
status: covered
---

# The sender cannot accept their own request

- Given: A->B pending
- When: A accepts it
- Then: rejected with the not-recipient reason, still pending
