---
feature: connection-requests
type: functional
priority: high
source: D-34
automated_test: tests/connections/send-request.test.ts::rejects a send between members connected through the decliner's request as already-connected
status: covered
---

# A send after the decliner's request was accepted is already-connected

- Given: A->B declined, then B->A accepted
- When: either member sends to the other
- Then: it is rejected as already-connected (the current state wins), nothing is stored
