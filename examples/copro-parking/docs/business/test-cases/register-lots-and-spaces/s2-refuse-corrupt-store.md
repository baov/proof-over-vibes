---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_json_repository.py::test_a_corrupt_store_is_reported_on_read_and_on_every_write_and_never_overwritten
status: covered
source: decisions.md D-19 (S1 carried over)
---

# A corrupt store is reported, never overwritten

Given a store file that is not valid JSON or lacks the expected shape, when the manager lists, registers or corrects, then a named "store unreadable" error is raised and the file content is identical afterwards.
