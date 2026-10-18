---
feature: connection-requests
type: functional
priority: high
source: bug brief bug-unrelated-members-connected; D-26 (erase leaves nothing about the member); D-15
automated_test: tests/connections/colliding-member-ids.test.ts::keeps two connections apart, so erasing a member ends only the connection that member is in
status: covered
---

# Two connections whose member ids look alike stay separate

- Given: `ann:bo` and `cy` connected, and `ann` and `bo:cy` connected
- When: `ann:bo` is erased
- Then: `ann:bo` and `cy` have no state any more, and `ann` and `bo:cy` are still connected
