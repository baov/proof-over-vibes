---
feature: connection-requests
type: functional
priority: high
source: PRD R13
automated_test: tests/connections/send-request.test.ts::accepts a new request each time after a withdrawal, however many times
status: covered
---

# Withdraw and resend can be repeated any number of times

- Given: A sends to B and withdraws, three times
- When: A sends to B each time
- Then: each is accepted with a different id and the pending list holds at most the live request
