---
role: orchestrator
status: done
reasons: []
---

# Metrics: price a cart, story 1 (price-without-promotion)

- first-review-go: yes (verdict GO at iteration 0)
- iterations: 0 NO-GO (1 review)
- failure-analyst-ran: no
- escalated: yes, by the Reviewer (the diff creates the declared sensitive zone domain.money / domain.pricing). A person's review is pending
- delegated-decisions: D-16..D-21 and D-25..D-32 so far (`answered-by-delegate`); human answers D-1..D-15, D-22..D-24
- pending-decisions: 0
- sensitive-zones: declared
- open-majors: 2 (negative amounts accepted, giving a negative total; overflow surfaces as a raw ArithmeticException), carried to story 2 and reserved for the edge-case request
- mutation: 91.7% (11/12), scope critical, no threshold; one survivor unreachable through the entry point; default PIT mutators do not touch Math.*Exact
- regression:
