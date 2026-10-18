---
feature: connection-requests
type: functional
priority: high
source: PRD R13
automated_test: tests/connections/send-request.test.ts::lets the sender send again after withdrawing: a new pending request, the old one not listed
status: covered
---

# After a withdrawal, the sender can send again

- Given: A->B withdrawn
- When: A sends to B again
- Then: a new request is pending (state pending) and it is the only one in B's pending list
