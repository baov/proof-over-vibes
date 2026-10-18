---
feature: connection-requests
type: functional
priority: high
source: D-25, PRD R7
automated_test: tests/connections/send-request.test.ts::rejects a request whose generated id is already used, and leaves the existing request unchanged
status: covered
---

# An id already in use is rejected, nothing is overwritten

- Given: A->B pending, and the id generator returns the id of that request again
- When: C sends a request to B
- Then: the send is rejected as "request-id-taken", the existing request is unchanged and C has no state with B
