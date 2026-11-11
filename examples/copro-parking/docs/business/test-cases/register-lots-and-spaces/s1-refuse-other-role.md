---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_any_other_role_is_refused_first_whatever_the_request
status: covered
source: stories.md S1 AC8
---

# Refuse any role other than manager

Given a non-manager actor, when registering a lot or a space, then it is refused with a manager-only refusal.

The manager-only refusal wins even when the value is also blank or a duplicate (D-16).
