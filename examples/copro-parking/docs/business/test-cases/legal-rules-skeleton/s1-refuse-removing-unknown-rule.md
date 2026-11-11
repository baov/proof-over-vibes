---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_an_unknown_or_already_removed_rule_is_refused
status: covered
source: stories.md S1 AC7
---

# Removing an unknown rule is refused

Given no rule "Z9", or a rule already removed, when the manager removes it, then it is refused as "unknown rule" and the rules are unchanged.
