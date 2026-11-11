---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_json_rule_repository.py::test_rules_survive_a_re_read_after_add_change_and_remove
status: covered
source: stories.md S1 AC11
---

# Rules survive a restart

Given rules added, changed and removed through one repository on a file, when a new repository reads the same file, then it lists the same rules in the same order, with the registration order kept.
