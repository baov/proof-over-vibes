---
role: orchestrator
status: done
reasons: []
---

# Metrics: price a cart, story 2 (apply-a-promotion)

- first-review-go: yes (verdict GO at iteration 0)
- iterations: 0 NO-GO (1 review)
- failure-analyst-ran: no
- escalated: yes, by the Reviewer (the diff touches the declared money sensitive zone). A person's review is pending
- delegated-decisions: D-35 and D-36 in this story (`answered-by-delegate`); human answers D-33 and D-34
- pending-decisions: 0
- sensitive-zones: declared
- open-majors: 3, all about amounts the PRD reserves: scales 10 to 18 accepted but unusable for ordinary amounts (overflow in subtotal x numerator); negative quantity, unit price, fee and minimum accepted; overflow surfaces as a raw ArithmeticException. Carried to the edge-case requests
- mutation: 98.0% (48/49), scope critical, no threshold; one survivor (a getter used only in an error message); default PIT mutators do not touch Math.*Exact, so sums are protected by behavior tests only
- regression:
