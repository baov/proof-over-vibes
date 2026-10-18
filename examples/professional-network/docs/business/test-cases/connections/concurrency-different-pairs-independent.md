---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/concurrency.test.ts::lets simultaneous operations on different pairs all succeed
status: covered
---

# Operations on different pairs do not disturb each other

- Given: Nobody has a request
- When: A sends to B and C sends to D at the same moment
- Then: both succeed and each recipient has one pending request
