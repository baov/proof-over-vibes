---
feature: connection-requests
type: functional
priority: high
source: PRD R1, R3, D-19
automated_test: tests/connections/blank-member-id.test.ts::rejects a state query with a blank member on either side, also the same blank twice
status: covered
---

# A state query with a blank member id is rejected

- Given: A->B pending
- When: the state is asked with a blank member on either side, or the same blank twice
- Then: blank-member-id; the same non-blank member twice still reports none (D-19)
