---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_the_manager_removes_a_space_found_ignoring_case_and_spaces_and_never_its_lot
status: covered
source: stories.md S3 AC1
---

# Remove a space

Given space "P1" on lot "A12" and "P2", when the manager removes " p1 " (found ignoring case and surrounding spaces), then the listing no longer shows P1 and still shows P2; the removal is still there when the register is read again.
