---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_a_minimum_only_a_maximum_only_or_both_are_accepted
status: covered
source: stories.md S1 AC2
---

# A minimum only, a maximum only, or both are accepted

Given the manager, when adding a rule with a minimum only, a maximum only, or both (equal bounds included), then each is accepted. A bound of 1 day is accepted. Bounds are inclusive (D-36); the evaluation itself comes with S2.
