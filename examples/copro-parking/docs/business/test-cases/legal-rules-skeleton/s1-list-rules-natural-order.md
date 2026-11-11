---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_listing_follows_the_natural_case_folded_order
status: covered
source: stories.md S1 AC8
---

# Anyone lists the rules in natural name order

Given rules "R10", "r2" and "a01", "A1" registered in any order, when any role lists the rules, then each shows name, kind, parameter and note, in natural case-folded order (r2 before R10), ties in registration order (a01 before A1 if registered first), whatever the configuration order (D-33). A change keeps the registration order; a removed and re-added rule counts as registered last. An empty list is returned when there is no rule.
