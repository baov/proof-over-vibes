---
feature: connection-requests
type: functional
priority: high
source: PRD R1, ADR-0002
automated_test: tests/connections/concurrency.test.ts::gives the outcome of erase first or erase last when a member is erased during another operation
status: covered
---

# Erasing a member during another operation

- Given: A->B pending, or nobody has a request
- When: A is erased while B accepts, or while A sends to B (or while A is erased again)
- Then: the outcome is that of erase first or erase last: no connection to an erased member, no request without its owner; the erase answers ok each time
