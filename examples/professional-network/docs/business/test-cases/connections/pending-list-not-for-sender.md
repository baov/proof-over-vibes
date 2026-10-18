---
feature: connection-requests
type: functional
priority: high
source: PRD R6
automated_test: tests/connections/pending-requests.test.ts::does not show a request to its sender
status: covered
---

# A sender does not see their request in their own pending list

- Given: A->B pending
- When: A asks for their pending requests
- Then: the list is empty (the request is addressed to B)
