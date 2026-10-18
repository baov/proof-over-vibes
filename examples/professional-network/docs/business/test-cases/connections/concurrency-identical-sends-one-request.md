---
feature: connection-requests
type: functional
priority: high
source: PRD R5
automated_test: tests/connections/concurrency.test.ts::creates one request and rejects the others as duplicate-pending when the same send is made at once
status: covered
---

# The same send made twice at once creates one request

- Given: Nobody has a request
- When: A sends to B two or three times at the same moment
- Then: exactly one send succeeds and the others are rejected as duplicate-pending; B has one pending request; the next send gets the second id
