---
feature: connection-requests
type: functional
priority: high
source: D-26
automated_test: tests/connections/erase-member.test.ts::succeeds when the member is erased twice, or was never known, and changes nothing
status: covered
---

# Erasing twice, or an unknown member, succeeds

- Given: A->B pending
- When: the module is told to erase C, then A twice
- Then: each call succeeds and nothing else changes
