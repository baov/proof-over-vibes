---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/blank-member-id.test.ts::does not draw a request id for a rejected blank send
status: covered
---

# A rejected blank send uses no request id

- Given: blank sends have been rejected
- When: A sends to B
- Then: the request gets the first id, as if the blank sends never happened
