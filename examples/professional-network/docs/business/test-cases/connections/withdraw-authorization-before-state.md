---
feature: connection-requests
type: functional
priority: high
source: D-13
automated_test: tests/connections/withdraw-request.test.ts::tells a member who is not the sender so, even if the request is no longer pending
status: covered
---

# A non-sender withdrawing a non-pending request gets the authorization reason

- Given: requests that are accepted, declined and withdrawn
- When: a non-sender tries to withdraw each one
- Then: each is rejected as not-sender, not as not-pending
