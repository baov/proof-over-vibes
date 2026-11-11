---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_repository.py::test_unreadable_offers_stop_a_renumbering_and_a_removal_and_both_files_stay_identical
status: covered
source: stories.md S4 AC1; decisions.md D-19
---

# Unreadable offers stop a removal

Given an unreadable offers file, removing a registered space that is not rented ends with the offers unreadable error (a store error, not a refusal), and the register and the offers file are byte-identical. An error of any other kind raised by the offers check is not swallowed: nothing is removed.
