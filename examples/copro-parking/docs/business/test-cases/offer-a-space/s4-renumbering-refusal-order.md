---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_the_register_refusals_come_before_space_offered
status: covered
source: stories.md S4 AC6; decisions.md D-71
---

# Renumbering refusals apply in a fixed order

The order is: not allowed, blank new number, unknown space, duplicate new number, space offered. Each pair is tested with both fitting. The offers are read only after the register's own checks passed, and asked once with the old number of the space.
