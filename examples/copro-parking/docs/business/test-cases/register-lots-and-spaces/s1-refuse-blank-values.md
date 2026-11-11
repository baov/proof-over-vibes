---
feature: register-lots-and-spaces
type: functional
priority: medium
automated_test: tests/test_use_cases.py::test_a_blank_lot_identifier_or_space_number_is_refused
status: covered
source: stories.md S1 AC7c
---

# Refuse blank identifier or number

Given a blank lot identifier or a blank space number, when the manager registers it, then it is refused.

The refusal is a named application error under the Refusal base (D-14).
