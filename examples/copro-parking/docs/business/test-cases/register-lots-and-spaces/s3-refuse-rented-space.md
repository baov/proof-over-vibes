---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_a_rented_space_is_refused_and_stays_listed
status: covered
source: stories.md S3 AC3
---

# Refuse removing a space with a rental

Given a space for which the rental port answers "has a rental" (existing or planned), when the manager removes it, then it is refused (space rented), the space stays registered and the register and its file are unchanged. With the default port ("no rental" until E3) the removal goes through.
