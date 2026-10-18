---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/blank-member-id.test.ts::rejects a send whose sender is blank, and stores nothing
status: covered
---

# A send from a blank member id is rejected

- Given: a sender id that is empty, spaces, a tab or a line break
- When: the member sends a request to B
- Then: it is rejected as blank-member-id and nothing is stored
