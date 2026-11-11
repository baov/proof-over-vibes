---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_dates_are_date_objects_or_iso_text_with_surrounding_spaces_ignored
status: covered
source: decisions.md D-60
---

# Accepted date forms

A date object or text YYYY-MM-DD with surrounding spaces is accepted; a datetime and any other form are an invalid date.
