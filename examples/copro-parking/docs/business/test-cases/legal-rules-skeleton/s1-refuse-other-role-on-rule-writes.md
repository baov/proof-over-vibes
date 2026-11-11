---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_any_other_role_is_refused_first_with_nothing_read_or_written
status: covered
source: stories.md S1 AC9
---

# Any role other than manager is refused on add, change and remove

Given a non-manager actor (owner, resident, missing or other value), when adding, changing or removing a rule, then it is refused as manager-only, even when the name is blank, a duplicate, unknown, or the parameter is invalid (D-16); nothing is read or validated first and the rules are unchanged.
