---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_a_refusal_leaves_the_file_identical
status: covered
source: stories.md S1 AC11
---

# A refusal leaves the offers unchanged

After any refusal the offers file bytes, the register and the list are identical; a refusal on first use creates no file.
