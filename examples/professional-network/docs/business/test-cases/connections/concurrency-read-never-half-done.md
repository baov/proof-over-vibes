---
feature: connection-requests
type: functional
priority: high
source: PRD R4
automated_test: tests/connections/concurrency.test.ts::never shows a request accepted without its connection to a read made during the accept
status: covered
---

# A read never sees half an operation

- Given: A->B pending
- When: the state of the pair or the pending list of B is read while B accepts (or A withdraws) the request
- Then: the answer is entirely the state before the operation or entirely the state after it; an accepted request is never seen without the connection
