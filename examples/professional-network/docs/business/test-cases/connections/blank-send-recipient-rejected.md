---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/blank-member-id.test.ts::rejects a send whose recipient is blank, and stores nothing
status: covered
---

# A send to a blank member id is rejected

- Given: a recipient id that is empty, spaces, a tab or a line break
- When: A sends a request to it
- Then: it is rejected as blank-member-id and nothing is stored
