---
feature: connection-requests
type: functional
priority: high
source: PRD R15, D-8, D-13
automated_test: tests/connections/pair-state.test.ts::is left unchanged by rejected attempts to accept
status: covered
---

# A rejected accept leaves the state of the pair unchanged

- Given: A->B pending, then accepted
- When: a non-recipient accepts, and later the request is accepted again
- Then: the state of the pair is unchanged each time
