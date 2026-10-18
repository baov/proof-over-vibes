---
feature: connection-requests
type: functional
priority: high
source: PRD R2
automated_test: tests/connections/blank-member-id.test.ts::treats an empty id, spaces, tabs and line breaks as blank
status: covered
---

# Empty, spaces, tabs and line breaks are blank

- Given: an id that is empty, or only spaces, tabs or line breaks
- When: it is used in a send or a state query
- Then: it is rejected as blank-member-id
