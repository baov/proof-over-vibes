---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_withdrawing_the_same_offer_twice_refuses_the_second_call
status: covered
source: stories.md S3 AC3
---

# Edges of a withdrawal request

Withdrawing twice refuses the second as unknown offer; nothing as offerer or number is invalid input; number 1 and the highest number work; withdrawing 1 then 2 or 2 then 1 gives the same list; withdrawing then offering again on the same days works.
