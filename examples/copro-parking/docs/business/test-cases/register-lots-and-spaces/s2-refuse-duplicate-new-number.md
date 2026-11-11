---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_a_new_number_already_used_is_refused
status: covered
source: stories.md S2 AC3
---

# Refuse a new number already used

Given spaces P1 and P2, when the manager changes P2 to " p1 " (any lot), then it is refused as a duplicate space and the register, listing and stored file, is unchanged. Changing a space to its own number in another case is not a duplicate.
