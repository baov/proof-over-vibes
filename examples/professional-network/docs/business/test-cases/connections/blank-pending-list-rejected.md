---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/blank-member-id.test.ts::rejects a pending list for a blank member
status: covered
---

# A pending list for a blank member id is rejected

- Given: B has a pending request
- When: the pending list of a blank member is asked
- Then: blank-member-id
