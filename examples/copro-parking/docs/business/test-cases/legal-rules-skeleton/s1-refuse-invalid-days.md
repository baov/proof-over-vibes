---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_zero_negative_or_non_whole_days_are_refused
status: covered
source: stories.md S1 AC3
---

# Invalid days or a minimum above the maximum are refused

Given the manager, when adding a rule whose minimum or maximum is zero, negative, or not a whole number of days, or whose minimum is above its maximum, then it is refused with a named reason (not-a-positive-number, minimum above maximum) and the rules are unchanged. A minimum equal to the maximum is accepted. The same holds when changing a rule.
