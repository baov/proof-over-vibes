---
feature: connection-requests
type: functional
priority: high
source: PRD R8
automated_test: tests/connections/send-request.test.ts::rejects a request a member sends to themselves, and stores nothing
status: covered
---

# Sending a request to oneself is rejected

- Given: a member
- When: they send a request to themselves
- Then: it is rejected with the self-request reason and nothing is stored
