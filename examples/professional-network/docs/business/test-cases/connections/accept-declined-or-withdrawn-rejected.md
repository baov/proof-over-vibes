---
feature: connection-requests
type: functional
priority: high
source: PRD R15, D-8
automated_test: tests/connections/accept-request.test.ts::rejects accepting a request that was declined or withdrawn, and the state is unchanged
status: covered
---

# Accept on a declined or withdrawn request is rejected, state unchanged

- Given: A->B declined and C->B withdrawn
- When: B tries to accept each one
- Then: each is rejected as not-pending and the states are unchanged
