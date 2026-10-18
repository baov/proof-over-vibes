---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/concurrency.test.ts::connects the pair once when the recipient accepts twice at once
status: covered
---

# Accepting twice at once connects the pair once

- Given: A->B pending
- When: B accepts the request twice at the same moment
- Then: exactly one accept succeeds and the other is rejected as not-pending; the pair is connected once, and a later send between them is rejected as already-connected
