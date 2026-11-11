---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_json_rule_repository.py::test_a_missing_or_blank_file_lists_nothing_and_is_not_created_by_reading
status: covered
source: stories.md S1 AC12
---

# A new installation has no rule

Given a missing or empty rules file, when listing, then no rule is returned, and no legal content is in the code, the data or the texts (the file is created only by the first successful write).
