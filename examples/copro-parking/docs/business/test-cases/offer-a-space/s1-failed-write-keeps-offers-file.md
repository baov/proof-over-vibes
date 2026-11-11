---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_a_failed_write_leaves_the_previous_file_intact_and_no_leftover
status: covered
source: ADR-0004 (atomic write, as ADR-0002)
---

# A failed write keeps the previous offers file

When replacing the file fails, the previous content is intact and no temporary file is left.
