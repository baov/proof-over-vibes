---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_a_blank_number_and_an_unknown_space_are_refused_before_the_offers_are_read
status: covered
source: stories.md S4 AC1; architect.md ADR-0004
---

# Removal refusals apply in a fixed order and the offers are asked last

The order is: not allowed, blank number, unknown space, space rented, space offered. Any other role is refused first and nobody is asked, even with unreadable offers. A blank number or an unknown space is refused before the offers are read. The offers are asked once, with the registered number, only for a known space that is not rented.
