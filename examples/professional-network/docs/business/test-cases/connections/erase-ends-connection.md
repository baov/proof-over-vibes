---
feature: connection-requests
type: functional
priority: high
source: architect
automated_test: tests/connections/erase-member.test.ts::ends the connection of an erased member, and the other member can send a request again
status: covered
---

# Erasing a connected member ends the connection

- Given: A and B connected
- When: the module is told to erase A
- Then: B has no state with A and can send a request to A
