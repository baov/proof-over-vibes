---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_a_removed_number_can_be_registered_again_on_any_lot
status: covered
source: stories.md S3 AC5
---

# A removed number can be registered again

Given space "P1" removed, when the manager registers "P1" again (on the same or another lot), then it is accepted and listed.
