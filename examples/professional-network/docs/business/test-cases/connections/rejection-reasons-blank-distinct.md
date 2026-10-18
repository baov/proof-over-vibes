---
feature: connection-requests
type: functional
priority: high
source: PRD R1
automated_test: tests/connections/rejection-reasons.test.ts::gives the blank member id rejection its own reason, distinct from the others
status: covered
---

# The blank member id reason is distinct from every other

- Given: a send, an accept and a state query with a blank member id, and the other rejected cases
- When: each is rejected
- Then: the blank ones all give blank-member-id and no other case gives it
