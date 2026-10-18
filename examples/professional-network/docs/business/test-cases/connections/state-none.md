---
feature: connection-requests
type: functional
priority: high
source: D-11
automated_test: tests/connections/pair-state.test.ts::is not connected with request state none when the two never exchanged a request
status: covered
---

# State of a pair with no request is none

- Given: two members who never exchanged a request
- When: the state is asked, in either order
- Then: not connected, request state none
