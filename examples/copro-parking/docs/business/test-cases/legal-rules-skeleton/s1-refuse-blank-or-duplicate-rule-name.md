---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_a_name_equal_ignoring_case_and_spaces_is_refused
status: covered
source: stories.md S1 AC4
---

# A blank or already used rule name is refused

Given a rule "Short stay", when the manager adds a rule with a blank, whitespace-only or missing name, or named " short STAY ", then it is refused (blank value, duplicate rule) and the rules are unchanged. Adding the same rule twice refuses the second.
