---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_register.py::test_a_space_on_an_unknown_lot_is_refused
status: covered
source: stories.md S1 AC6
---

# Refuse a space on an unknown lot

Given no lot "Z9", when the manager registers a space on it, then it is refused.

The refusal is a named application error under the Refusal base (D-14).
