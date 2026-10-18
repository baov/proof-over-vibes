---
feature: connection-requests
type: functional
priority: high
source: PRD R1, D-13
automated_test: tests/connections/concurrency.test.ts::gives a rejected operation its own reason and leaves the simultaneous valid one untouched
status: covered
---

# A rejected operation beside a valid one

- Given: A->B may be pending
- When: an operation the rules reject (blank member id, unknown request id) is made at the same moment as a valid one
- Then: the rejected one gets its own reason, exactly as alone; the valid one succeeds as alone
