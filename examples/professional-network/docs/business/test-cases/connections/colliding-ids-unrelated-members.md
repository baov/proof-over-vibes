---
feature: connection-requests
type: functional
priority: high
source: bug brief bug-unrelated-members-connected; D-15 (member ids are free strings)
automated_test: tests/connections/colliding-member-ids.test.ts::does not show two unrelated members as connected, and lets one send to the other
status: covered
---

# Unrelated members are not shown as connected because their ids look alike

- Given: `ann:bo` and `cy` connected; `ann` and `bo:cy` have never interacted (the ids are the same characters once joined with a colon)
- When: the state of `ann` and `bo:cy` is read, then `ann` sends to `bo:cy`
- Then: the state is not connected with no request, and the send succeeds with a pending request
