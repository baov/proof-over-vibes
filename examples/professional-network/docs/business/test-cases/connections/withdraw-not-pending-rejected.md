---
feature: connection-requests
type: functional
priority: high
source: PRD R15, D-8
automated_test: tests/connections/withdraw-request.test.ts::rejects withdrawing a request that is no longer pending, and the state is unchanged
status: covered
---

# Withdraw on a non-pending request is rejected, state unchanged

- Given: requests that are accepted, declined and withdrawn
- When: the sender tries to withdraw each one
- Then: each is rejected as not-pending and the state of each pair is unchanged (acting twice included)
