---
feature: connection-requests
type: functional
priority: high
source: D-19
automated_test: tests/connections/pair-state.test.ts::is not connected with request state none for a member and themselves
status: covered
---

# State of a member with themselves is none, not connected

- Given: a member
- When: their state with themselves is asked
- Then: not connected, request state none; the query does not reject
