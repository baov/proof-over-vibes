---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_a_number_or_identifier_already_used_is_refused_on_any_lot
status: covered
source: stories.md S1 AC5
---

# Refuse a duplicate space number

Given space "P1", when the manager registers " p1 " on any lot, then it is refused as a duplicate and the register is unchanged.

The refusal is a named application error under the Refusal base (D-14).
