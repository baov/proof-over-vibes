---
feature: connection-requests
type: functional
priority: high
source: D-12
automated_test: tests/connections/pair-state.test.ts::reports the live request when the pair has several, otherwise the most recent
status: covered
---

# With several requests the state is the live one, else the most recent

- Given: A->B withdrawn, then sent again, withdrawn again, sent again and accepted
- When: the state is read after each step
- Then: withdrawn, pending, withdrawn, then connected with accepted
