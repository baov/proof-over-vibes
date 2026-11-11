---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_a_refusal_leaves_the_file_identical_or_uncreated
status: covered
source: stories.md S3 AC5
---

# A refused withdrawal changes nothing

After each refusal the list, the register and the offers file bytes are unchanged, the next number included, and the offers store has not been saved.
