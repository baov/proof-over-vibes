---
feature: connection-requests
type: functional
priority: high
source: D-14
automated_test: tests/connections/erase-member.test.ts::keeps the decline block when a third member is erased
status: covered
---

# Erasing a third member does not lift the block

- Given: A->B declined
- When: the module is told to erase C
- Then: A sending to B is still rejected as previously-declined
