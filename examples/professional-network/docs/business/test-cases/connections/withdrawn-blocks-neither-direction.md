---
feature: connection-requests
type: functional
priority: high
source: PRD R10, R13
automated_test: tests/connections/send-request.test.ts::does not let a withdrawn request block the other member from sending
status: covered
---

# A withdrawn request blocks neither direction

- Given: A->B withdrawn
- When: B sends to A
- Then: it is accepted
