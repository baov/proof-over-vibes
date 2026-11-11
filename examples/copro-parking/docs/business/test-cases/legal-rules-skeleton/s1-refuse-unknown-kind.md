---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_an_unknown_or_missing_kind_is_refused
status: covered
source: stories.md S1 AC5
---

# An unknown kind is refused

Given the manager, when adding a rule of a kind that is not on the closed list (any text other than the two kinds, a missing kind), then it is refused with a named "unknown kind" reason and the rules are unchanged. At this story only duration bounds can be added; owner consent comes with S3.
