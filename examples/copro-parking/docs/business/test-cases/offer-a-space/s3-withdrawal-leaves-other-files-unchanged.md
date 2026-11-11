---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_withdrawing_leaves_the_register_file_and_the_rules_file_bytes_unchanged
status: covered
source: stories.md S3 AC5
---

# A withdrawal does not touch the register or rules files

The bytes of the register file and the rules file are identical before and after a withdrawal.
