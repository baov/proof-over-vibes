---
feature: connection-requests
type: functional
priority: high
source: PRD R7
automated_test: tests/connections/rejection-reasons.test.ts::gives every rejected case its own reason
status: covered
---

# Each rejection has a distinct reason

- Given: the seven rejected cases of sending and accepting
- When: their reasons are collected
- Then: they are pairwise distinct and each is the one named for its rule
