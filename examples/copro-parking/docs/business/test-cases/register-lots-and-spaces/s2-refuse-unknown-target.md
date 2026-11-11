---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_an_unknown_lot_or_space_is_refused
status: covered
source: stories.md S2 AC4
---

# Refuse changing an unknown lot or space

Given a register without lot Z9 and without space P7, when the manager changes the owner of Z9 or the number of P7, then it is refused (unknown lot, unknown space) and the register is unchanged. Targets are found ignoring case and surrounding spaces.
