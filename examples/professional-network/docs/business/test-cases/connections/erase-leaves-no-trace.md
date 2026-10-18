---
feature: connection-requests
type: functional
priority: high
source: architect, D-14
automated_test: tests/connections/erase-member.test.ts::leaves no request, connection or list entry that involves the erased member
status: covered
---

# Erasing a member leaves no trace of them

- Given: A has pending requests in both directions and a connection, B and C are connected to each other
- When: the module is told to erase A
- Then: A has no request, connection or list entry with anyone, and the relation between B and C is untouched
