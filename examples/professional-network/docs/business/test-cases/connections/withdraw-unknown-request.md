---
feature: connection-requests
type: functional
priority: high
source: D-16, D-31
automated_test: tests/connections/withdraw-request.test.ts::rejects withdrawing a request that is not found, whoever asks
status: covered
---

# Decline or withdraw on an unknown request is rejected, whoever acts

- Given: no request has this id
- When: A or C tries to withdraw it
- Then: it is rejected as request-not-found, whoever acts
