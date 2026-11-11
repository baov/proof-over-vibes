---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_an_unknown_space_is_refused_and_so_is_a_second_removal
status: covered
source: stories.md S3 AC2
---

# Refuse removing an unknown space

Given a register without space "P7", when the manager removes "P7", or removes "P1" a second time, then it is refused (unknown space) and the register is unchanged. A blank or missing number is refused as blank (D-12).
