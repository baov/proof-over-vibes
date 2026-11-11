---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_a_blank_value_is_refused_as_blank
status: covered
source: stories.md S2 AC3b
---

# Refuse a blank new number or owner

Given an existing lot and space, when the manager changes the owner or the number to a blank, whitespace-only or missing value, then it is refused as a blank value and the register is unchanged.
