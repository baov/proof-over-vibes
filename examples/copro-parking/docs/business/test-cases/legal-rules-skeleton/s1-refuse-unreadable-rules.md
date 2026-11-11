---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_json_rule_repository.py::test_unreadable_rules_are_reported_on_read_and_every_write_and_never_overwritten
status: covered
source: stories.md S1 AC13
---

# Unreadable rules are reported and never overwritten

Given a rules file that is not valid JSON, has the wrong shape, an unknown kind, an invalid parameter or a duplicate name, when listing, adding, changing or removing, then a named "rules unreadable" error is raised (a StoreUnreadable, not a Refusal) and the file content is identical afterwards (D-19, D-35). Each write use case raises it before anything is written.
