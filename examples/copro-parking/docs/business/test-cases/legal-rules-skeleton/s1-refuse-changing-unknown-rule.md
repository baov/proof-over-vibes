---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_an_unknown_rule_is_refused
status: covered
source: stories.md S1 AC6
---

# Changing an unknown rule is refused

Given no rule "Z9", when the manager changes "Z9", then it is refused as "unknown rule" and the rules are unchanged.
