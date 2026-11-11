---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_a_lot_without_owner_is_refused
status: covered
source: stories.md S1 AC3
---

# Refuse a lot without owner

Given a lot with no owner or a blank owner name, when the manager registers it, then it is refused.

The refusal is a named application error under the Refusal base (D-14).
