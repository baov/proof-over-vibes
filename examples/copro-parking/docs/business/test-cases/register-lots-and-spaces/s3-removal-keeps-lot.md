---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_the_manager_removes_a_space_found_ignoring_case_and_spaces_and_never_its_lot
status: covered
source: stories.md S3 AC6
---

# Removing a space never removes its lot

Given lot "A12" with the single space "P1", when the manager removes "P1", then lot "A12" with its owner still appears in the listing, with no space.
