---
feature: connection-requests
type: functional
priority: high
source: PRD R14
automated_test: tests/connections/send-request.test.ts::limits the decline block to that pair: the sender may ask others, others may ask the decliner
status: covered
---

# The decline block is for the pair only

- Given: A->B declined
- When: A sends to C, and C sends to B
- Then: both are accepted
