---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_a_given_parameter_replaces_the_whole_one_and_a_missing_one_keeps_it
status: covered
source: decisions.md D-39
---

# Changing the parameter replaces it as a whole

Given a rule with minimum 30 and maximum 365, when the manager changes its parameter to a maximum of 200 only, then the rule has no minimum and a maximum of 200. A change with no parameter keeps both bounds. A given parameter with neither bound is refused.
