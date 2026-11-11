---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_repository.py::test_unreadable_offers_stop_a_renumbering_and_both_files_stay_identical
status: covered
source: stories.md S4 AC6; decisions.md D-19
---

# Unreadable offers stop a renumbering

Given an unreadable offers file, a valid renumbering ends with the offers unreadable error, and the register and the offers file are byte-identical. An error of any other kind raised by the offers check is not swallowed.
