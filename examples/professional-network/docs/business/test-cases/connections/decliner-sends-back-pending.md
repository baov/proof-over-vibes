---
feature: connection-requests
type: functional
priority: high
source: PRD R5
automated_test: tests/connections/send-request.test.ts::lets the decliner send a request back, pending, and keeps the declined request as it was
status: covered
---

# The decliner can send a request back

- Given: A->B was declined by B
- When: B sends a request to A
- Then: it is accepted and pending, A sees it in the pending list, the declined request is unchanged
