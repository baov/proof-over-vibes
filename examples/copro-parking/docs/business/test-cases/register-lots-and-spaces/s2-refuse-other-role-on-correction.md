---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_any_other_role_is_refused_on_both_corrections
status: covered
source: stories.md S2 AC5
---

# Refuse any other role on a correction

Given an existing lot and space, when the owner, the resident, or a missing or unknown role changes an owner or a number, then it is refused as manager-only, before any other check (D-16), and the register is unchanged.
