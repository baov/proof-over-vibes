---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_json_repository.py::test_entries_survive_a_re_read_from_the_same_file
status: covered
source: stories.md S1 AC10
---

# Entries survive a re-read

Given registered entries, when the register is read again from the same file, then they are all there.
