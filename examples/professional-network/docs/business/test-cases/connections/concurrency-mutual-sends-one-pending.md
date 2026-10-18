---
feature: connection-requests
type: functional
priority: high
source: PRD R2, D-6
automated_test: tests/connections/concurrency.test.ts::creates one pending request and rejects the other as reverse-pending when two members send to each other at once, without connecting them
status: covered
---

# Two members sending to each other at once: one pending request

- Given: Nobody has a request
- When: A sends to B and B sends to A at the same moment
- Then: exactly one send succeeds and the other is rejected as reverse-pending; one pending request exists, shown to its recipient only; the pair is not connected (no automatic accept); either send may be the one that succeeds
