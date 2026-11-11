---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_json_repository.py::test_a_correction_survives_a_re_read_from_the_same_file
status: covered
source: stories.md S2 AC6, S1 AC10
---

# A correction survives a re-read

Given a changed owner and a changed number saved through the JSON repository, when a new repository reads the same file, then the listing shows the corrected values.
