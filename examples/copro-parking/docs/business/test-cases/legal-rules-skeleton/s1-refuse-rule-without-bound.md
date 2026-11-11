---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_a_rule_with_neither_bound_is_refused
status: covered
source: stories.md S1 AC2
---

# A rule with neither bound is refused

Given the manager, when adding a duration-bounds rule with no minimum and no maximum (no parameter, or an empty one), then it is refused with a named "no bound" reason and the rules are unchanged.
