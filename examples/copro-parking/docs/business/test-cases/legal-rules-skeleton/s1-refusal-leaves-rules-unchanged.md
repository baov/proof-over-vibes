---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_json_rule_repository.py::test_a_refusal_leaves_the_file_identical
status: covered
source: stories.md S1 AC10
---

# A refusal leaves the rules unchanged

Given stored rules, when any add, change or removal is refused, then the listing and the stored file are identical afterwards, and a refusal on first use creates no file.
