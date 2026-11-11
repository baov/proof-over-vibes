---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_the_manager_changes_a_space_number_keeping_its_lot
status: covered
source: stories.md S2 AC2, AC6
---

# Change a space's number

Given space P1 on lot A12, when the manager changes its number to " P9 ", then the listing shows P9 under A12 and P1 no longer exists; the space is found by its current number ignoring case and surrounding spaces.
