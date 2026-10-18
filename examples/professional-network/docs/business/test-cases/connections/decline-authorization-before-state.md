---
feature: connection-requests
type: functional
priority: high
source: D-13
automated_test: tests/connections/decline-request.test.ts::tells a member who is not the recipient so, even if the request is no longer pending
status: covered
---

# A non-recipient declining a non-pending request gets the authorization reason

- Given: requests that are accepted, declined and withdrawn
- When: a non-recipient tries to decline each one
- Then: each is rejected as not-recipient, not as not-pending
