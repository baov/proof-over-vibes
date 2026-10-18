---
feature: connection-requests
type: functional
priority: high
source: PRD R15, D-8
automated_test: tests/connections/decline-request.test.ts::rejects declining a request that is no longer pending, and the state is unchanged
status: covered
---

# Decline on a non-pending request is rejected, state unchanged

- Given: requests that are accepted, declined and withdrawn
- When: the right party tries to decline each one
- Then: each is rejected as not-pending and the state of each pair is unchanged (acting twice included)
