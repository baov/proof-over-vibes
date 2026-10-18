---
feature: connection-requests
type: functional
priority: high
source: PRD R10, D-6
automated_test: tests/connections/send-request.test.ts::rejects a request to a member who has a pending request to the sender, without accepting it
status: covered
---

# A reverse pending request is rejected, no automatic accept

- Given: A->B pending
- When: B sends to A
- Then: rejected with the reverse-pending reason; A->B is still pending and nothing else is created
