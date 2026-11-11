---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_a_duplicate_lot_is_refused
status: covered
source: stories.md S1 AC2
---

# Refuse a duplicate lot identifier

Given lot "A12", when the manager registers " a12 ", then it is refused as a duplicate and the register is unchanged.

The refusal is a named application error under the Refusal base (D-14).
