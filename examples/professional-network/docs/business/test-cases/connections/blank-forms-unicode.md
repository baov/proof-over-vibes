---
feature: connection-requests
type: functional
priority: high
source: PRD R2, D-33
automated_test: tests/connections/blank-member-id.test.ts::treats non-breaking and ideographic spaces as blank, and zero-width characters as not blank
status: covered
---

# Unicode spaces are blank, zero-width characters are not

- Given: an id made of a no-break space, an ideographic space or other Unicode spaces, or of a zero-width character
- When: it is used in a send
- Then: the Unicode spaces are rejected as blank-member-id; the zero-width id is accepted as a non-blank id (D-15)
