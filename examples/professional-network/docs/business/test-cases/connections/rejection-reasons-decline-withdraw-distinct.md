---
feature: connection-requests
type: functional
priority: high
source: PRD R7
automated_test: tests/connections/rejection-reasons.test.ts::gives the rejections of declining and withdrawing their own reasons, distinct from the others
status: covered
---

# Each new rejection has a distinct reason

- Given: the rejected cases of withdraw by the recipient, decline by the sender, unknown id, withdraw of a declined request, send after a decline, and an id already used
- When: their reasons are collected
- Then: they are pairwise distinct and each is the one named for its rule
