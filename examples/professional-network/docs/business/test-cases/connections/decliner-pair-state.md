---
feature: connection-requests
type: functional
priority: high
source: PRD R8, D-12
automated_test: tests/connections/pair-state.test.ts::reports the decliner's pending request over the earlier declined one, else the most recent
status: covered
---

# The pair state follows the decliner's request

- Given: A->B declined, then B->A sent
- When: the state is read from both sides after each step
- Then: declined, then pending, then declined or accepted with the connection
