---
feature: connection-requests
type: functional
priority: high
source: D-38
automated_test: tests/connections/concurrency.test.ts::lets the operations behind a failing one run normally and gives its caller the original error
status: covered
---

# A failing operation does not block the others

- Given: an operation that fails because something underneath fails (the request id generator throws)
- When: other operations are made at the same moment and afterwards
- Then: the failing operation's caller gets the same error, nothing was stored for it, and the others get their normal answers
