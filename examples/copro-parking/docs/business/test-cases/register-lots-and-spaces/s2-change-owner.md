---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_the_manager_changes_the_owner_keeping_the_spaces
status: covered
source: stories.md S2 AC1, AC6
---

# Change a lot's owner

Given lot A12 owned by Durand, when the manager changes its owner to " Martin ", then the listing shows A12 with owner "Martin" (trimmed, case kept, D-15) and its spaces are unchanged.
