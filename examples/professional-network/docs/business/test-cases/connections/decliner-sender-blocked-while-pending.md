---
feature: connection-requests
type: functional
priority: high
source: PRD R6, D-34
automated_test: tests/connections/send-request.test.ts::still rejects the original sender while the decliner's request is pending
status: covered
---

# The original sender still cannot send while the decliner request is pending

- Given: A->B declined, then B->A pending
- When: A sends to B, twice
- Then: it is rejected as reverse-pending both times and nothing is stored
