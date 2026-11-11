---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_a_space_has_an_open_offer_until_its_last_day_found_ignoring_case_and_spaces
status: covered
source: architect.md ADR-0004
---

# The stored offer check answers whether a space has an open offer

It answers true for an open offer of the space, found ignoring case and surrounding spaces, and for one ending today. It answers false, exactly false, for no offer, an offer of another space or an offer ended yesterday. It reads the clock once and the offers once per question. An unreadable offers file raises the offers unreadable error, never false.
