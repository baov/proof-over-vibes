---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_the_manager_registers_a_space_under_an_existing_lot
status: covered
source: stories.md S1 AC4
---

# Register a space on an existing lot

Given lot "A12", when the manager registers space "P1" on it, then the space is registered under that lot.
