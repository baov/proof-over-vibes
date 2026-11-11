---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_the_manager_registers_a_lot_with_its_owner
status: covered
source: stories.md S1 AC1
---

# Register a lot with one owner

Given an empty register, when the manager registers lot "A12" owned by "Durand", then the lot is in the register with that owner.

Listing shows the trimmed text as typed, case kept: registering " a12 " lists "a12" (D-15).
