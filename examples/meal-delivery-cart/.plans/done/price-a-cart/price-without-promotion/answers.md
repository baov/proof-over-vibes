---
role: product-owner
status: done
reasons: []
---

# Answers to the Planner (story 1)

All three are `answered-by-delegate`, relayed by the orchestrator, not read by a person.

1. Q1, negative or overflowing amounts: (a) leave reserved. No rule, no test; the natural behavior stays undocumented. Source: PRD section 6. Logged as D-30.
2. Q2, shape of the result: (a) named fields in R2 order: subtotal, discount, feeLine (absent for the empty cart), total. Source: PRD R2, R17, D-24. Logged as D-31.
3. Q3, non-empty cart with a zero subtotal: (a) accepted, the fee line still applies. Source: PRD R12, R17, R18. Logged as D-32.
