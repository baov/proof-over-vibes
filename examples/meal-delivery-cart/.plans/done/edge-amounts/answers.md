---
role: product-owner
status: done
reasons: []
---

# Answers to the Planner (edge-amounts)

All three are `answered-by-delegate`, relayed by the orchestrator, not read by a person.

1. Q1, other currency and amount too large together: (A) the currency refusal (IllegalArgumentException) always wins. D-42.
2. Q2, what the caller learns from 'amount too large': (A) the type alone, AmountTooLargeException in domain.money (an ArithmeticException); the message is for humans and does not name the amount. D-43.
3. Q3, public Money.times(rate) with a negative amount or negative rate numerator: (A) refused with IllegalArgumentException; zero accepted. D-44.
