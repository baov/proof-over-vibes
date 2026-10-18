---
feature: connection-requests
type: functional
priority: high
source: D-16
automated_test: tests/connections/accept-request.test.ts::rejects a request that is not found, whoever asks
status: covered
---

# Accept on an unknown request is rejected with its own reason

- Given: no request has this id
- When: a member accepts it
- Then: rejected with the request-not-found reason, whoever the member is
