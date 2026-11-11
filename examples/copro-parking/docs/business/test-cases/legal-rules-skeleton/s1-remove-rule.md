---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_a_removed_rule_disappears_and_its_name_is_free_again
status: covered
source: stories.md S1 AC7
---

# The manager removes a rule

Given a rule "Short stay", when the manager removes " short stay ", then it no longer appears in the listing and its name is free again.
