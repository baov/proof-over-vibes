---
feature: connection-requests
type: functional
priority: high
source: PRD R2, R4
automated_test: tests/connections/blank-member-id.test.ts::keeps an id with blanks around or inside real characters as it is
status: covered
---

# An id with blanks around or inside real characters is not blank

- Given: ids such as "a b" and " alice "
- When: they send a request to B
- Then: it is accepted and the id is kept as given, not trimmed
