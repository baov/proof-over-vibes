---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_any_other_role_is_refused_first_and_the_port_is_not_asked
status: covered
source: stories.md S3 AC4
---

# Refuse any role other than manager on removal

Given a non-manager actor (owner, resident, missing or unknown role), when removing a space, then it is refused with a manager-only refusal, checked first (D-16): even for an unknown space, a blank number or a space with a rental; the rental port is not asked.
