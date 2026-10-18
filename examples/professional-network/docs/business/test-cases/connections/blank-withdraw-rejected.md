---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/blank-member-id.test.ts::rejects a withdrawal by a blank member and leaves the request pending
status: covered
---

# A withdrawal by a blank member id is rejected

- Given: A->B pending
- When: a blank member withdraws it
- Then: it is rejected as blank-member-id and the request is still pending
