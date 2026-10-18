---
feature: connection-requests
type: functional
priority: high
source: PRD R3
automated_test: tests/connections/blank-member-id.test.ts::reports a send with both ids blank as blank-member-id, not as a request to oneself
status: covered
---

# Two blank ids are reported as blank, not as a request to oneself

- Given: both ids blank, identical or different
- When: the member sends
- Then: it is rejected as blank-member-id, never self-request
