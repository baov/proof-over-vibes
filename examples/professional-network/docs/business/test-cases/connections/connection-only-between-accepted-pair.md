---
feature: connection-requests
type: functional
priority: high
source: PRD R3, R5
automated_test: tests/connections/pair-state.test.ts::does not connect a member to anyone but the member they accepted
status: covered
---

# A connection links only the two members, not either of them to anyone else

- Given: A and B connected
- When: the state of A with C, B with C is asked, and C sends to B, A sends to C
- Then: none of them is connected, and the requests are accepted
