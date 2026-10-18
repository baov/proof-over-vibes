---
feature: connection-requests
type: functional
priority: high
source: D-13
automated_test: tests/connections/accept-request.test.ts::tells a member who is not the recipient they are not the recipient, even if the request is not pending
status: covered
---

# A non-recipient on a non-pending request gets the authorization reason

- Given: A->B accepted
- When: C accepts it
- Then: rejected with the not-recipient reason, not the not-pending one
