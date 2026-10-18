---
feature: connection-requests
type: functional
priority: high
source: D-14
automated_test: tests/connections/send-request.test.ts::keeps the decline block whatever else happens between other members
status: covered
---

# The decline block has no expiry and survives other activity

- Given: A->B declined, then other requests are sent and accepted between other members
- When: A sends to B again
- Then: it is still rejected as previously-declined
