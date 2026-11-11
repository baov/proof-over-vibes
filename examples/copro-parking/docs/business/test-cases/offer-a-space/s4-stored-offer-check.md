---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_no_offer_another_space_or_an_offer_ended_yesterday_answer_exactly_false
status: covered
source: architect.md ADR-0004
---

# The stored offer check answers whether a space has an open offer

It answers true for an open offer of the space, found ignoring case and surrounding spaces, and for one ending today. It answers false, exactly false, for no offer, an offer of another space or an offer ended yesterday. It reads the clock once and the offers once per question. An unreadable offers file raises the offers unreadable error, never false.
