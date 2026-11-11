---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_the_name_is_found_ignoring_case_and_spaces_and_name_and_kind_stay
status: covered
source: stories.md S1 AC6
---

# The manager changes a rule

Given a rule "Short stay", when the manager changes its parameter or its source note (name found ignoring case and surrounding spaces), then the listing shows the new values, the name and kind are unchanged, and the rule keeps its place among rules of the same natural name order. The new parameter is validated as for an addition (no bound, invalid days, minimum above maximum are refused, rules unchanged). Changing a rule to the values it already has is accepted (as D-21).
