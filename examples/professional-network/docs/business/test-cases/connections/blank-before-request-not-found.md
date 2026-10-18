---
feature: connection-requests
type: functional
priority: high
source: PRD R3
automated_test: tests/connections/blank-member-id.test.ts::reports a blank acting member before an unknown request id, on accept, decline and withdraw
status: covered
---

# A blank acting member is reported before an unknown request

- Given: no request with the given id
- When: a blank member accepts, declines or withdraws it
- Then: blank-member-id, not request-not-found
