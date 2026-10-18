---
feature: connection-requests
type: functional
priority: high
source: D-12
automated_test: tests/connections/pair-state.test.ts::reports declined, the most recent, when a withdrawn request came before the declined one
status: covered
---

# The most recent request wins over an older withdrawn one

- Given: A->B withdrawn, then sent again and declined
- When: the state is read
- Then: it is declined, from both members
