---
feature: connection-requests
type: functional
priority: high
source: PRD R6, D-18
automated_test: tests/connections/pending-requests.test.ts::lists only the requests addressed to the member, oldest first
status: covered
---

# Pending requests of a recipient: only theirs, oldest first

- Given: A->B, C->B, D->E pending, and B->D
- When: B asks for the requests pending for them
- Then: exactly A->B then C->B, not D->E, not the one B sent
