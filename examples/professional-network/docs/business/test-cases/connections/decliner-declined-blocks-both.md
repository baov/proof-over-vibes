---
feature: connection-requests
type: functional
priority: high
source: PRD R7, R14
automated_test: tests/connections/send-request.test.ts::blocks both members once the original sender declines the decliner's request
status: covered
---

# Declining the decliner's request blocks both directions

- Given: A->B declined, then B->A pending
- When: A declines it, then either member sends to the other
- Then: both are rejected as previously-declined and the state is declined from both sides
