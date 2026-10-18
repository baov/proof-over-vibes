---
feature: connection-requests
type: functional
priority: high
source: PRD R6
automated_test: tests/connections/pending-requests.test.ts::is an empty list for a member with no request
status: covered
---

# No pending request gives an empty list

- Given: a member with no request addressed to them
- When: they ask for their pending requests
- Then: the list is empty, not an error
