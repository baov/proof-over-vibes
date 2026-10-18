---
feature: connection-requests
type: functional
priority: high
source: PRD R12
automated_test: tests/connections/withdraw-request.test.ts::rejects a member who is not the sender, the recipient included, and the request stays pending
status: covered
---

# A non-sender or the recipient cannot withdraw, the request stays pending

- Given: A->B pending
- When: C, or B, tries to withdraw it
- Then: it is rejected as not-sender and the request is still pending
