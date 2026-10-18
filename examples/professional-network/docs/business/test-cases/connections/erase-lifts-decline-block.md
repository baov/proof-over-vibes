---
feature: connection-requests
type: functional
priority: high
source: PRD R14, D-14, architect
automated_test: tests/connections/erase-member.test.ts::lifts the decline block when either member of the declined pair is erased
status: covered
---

# Erasing either member of a declined pair lifts the block

- Given: A->B declined, and C->D declined
- When: the module is told to erase A, and to erase D
- Then: A can send to B again and C can send to D again
