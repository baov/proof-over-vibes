---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_the_manager_removes_a_space_found_ignoring_case_and_spaces
status: covered
source: stories.md S4 AC5
---

# Removal without an offer behaves as before

With no offer on the space, the removal keeps every earlier behavior: lookup ignoring case and spaces, nothing returned, the lot stays, the number can be registered again, unknown and blank numbers are refused, a second removal is refused.
