---
feature: connection-requests
type: functional
priority: high
source: PRD R2
automated_test: tests/connections/accept-request.test.ts::rejects a member who is not the recipient, and the request stays pending
status: covered
---

# A non-recipient cannot accept, the request stays pending

- Given: A->B pending
- When: C accepts it
- Then: rejected with the not-recipient reason, still pending
