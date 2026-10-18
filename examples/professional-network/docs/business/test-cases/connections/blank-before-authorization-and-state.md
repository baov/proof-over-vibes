---
feature: connection-requests
type: functional
priority: high
source: PRD R3, D-13
automated_test: tests/connections/blank-member-id.test.ts::reports a blank acting member before the not-recipient, not-sender and not-pending reasons
status: covered
---

# A blank acting member is reported before authorization and state

- Given: requests that are pending, withdrawn, declined or accepted
- When: a blank member accepts, declines or withdraws them
- Then: blank-member-id, not not-recipient, not-sender or not-pending
