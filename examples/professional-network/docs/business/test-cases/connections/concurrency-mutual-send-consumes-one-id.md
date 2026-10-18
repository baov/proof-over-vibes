---
feature: connection-requests
type: functional
priority: high
source: PRD R2, D-32
automated_test: tests/connections/concurrency.test.ts::draws a request id only for the send that wins a mutual send
status: covered
---

# A rejected mutual send uses no request id

- Given: A and B send to each other at the same moment
- When: a third pair then sends
- Then: the next request gets the second id, as if the rejected send had never happened
