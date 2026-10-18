---
feature: connection-requests
type: functional
priority: high
source: PRD R2
automated_test: tests/connections/decline-request.test.ts::rejects a member who is not the recipient, the sender included, and the request stays pending
status: covered
---

# A non-recipient or the sender cannot decline, the request stays pending

- Given: A->B pending
- When: C, or A, tries to decline it
- Then: it is rejected as not-recipient and the request is still pending
