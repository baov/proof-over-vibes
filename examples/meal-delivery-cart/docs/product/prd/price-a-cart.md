# PRD: price a cart

Status: ready. Q1 to Q4 answered and read by the human; Q5 answered by the orchestrator on my recommendation (delegated, not read by a person: the human may overturn it). Backlog items 4 to 7 (*picked*). Serves vision outcome O1 (cart total equals order total); makes O2 and O3 possible later.

## 1. Problem

Customers meet the final price late and spread over several lines (`research.md`, section 1, *unverified* as a felt pain). Nothing downstream can show a trustworthy total until one place computes it from the cart, one fee line and one promotion.

## 2. Goal and success

Given a cart, the fee and promotion rules, produce one price: every line visible and the total exact, the same every time. Success: for any cart, the total shown equals the total later confirmed (O1). No target figure is set.

## 3. Users and use

Caller: whatever shows or confirms a cart (display and order handoff are other features). Main path: the caller supplies the cart lines (unit price, quantity), the money rules and optionally one promotion code; it receives the breakdown and total.

## 4. Scope

In: pricing a cart as pure domain behavior; money rules as parameters (currency, fee rule, promotion rule); one fee line; one promotion type; the full breakdown.
Out: UI, payment, order handoff, catalogue, adding/removing dishes, tax, tip, extra fee lines, promotion variants, subscriptions, multiple carts.

## 5. Requirements (each observable from outside)

Independent of the open questions:
- R1. The subtotal is the sum over lines of unit price times quantity.
- R2. The result exposes every line: subtotal, discount, fee line, total.
- R3. The total is computed only from the cart, the rules and the code supplied; the same input always gives the same result.
- R4. No amount, rate, threshold or currency is built in: each comes from the rules supplied.
- R5. Pricing does not change the cart.
- R6. Changing a rule parameter changes the result with no other change.

Promotion (Q1, Q2):
- R7. A promotion is a percentage off the food subtotal; the rate is a parameter of the rules.
- R8. The discount is the subtotal times the rate, rounded as in R14.
- R9. A code that is unknown, or a subtotal below the minimum parameter, gives a result with no discount and the reason stated in the result; pricing still succeeds.
- R10. The discount never exceeds the subtotal; the food total after discount is never below zero.
- R11. Without a code, the discount is zero.

Fee (Q3):
- R12. The fee line is one flat delivery fee, a parameter, the same whether or not a promotion applies.
- R13. The promotion discounts food only, never the fee. Total = subtotal - discount + fee.

Money (Q4):
- R14. Each computed amount (discount, fee) is rounded once, half up, to the currency's smallest unit; the subtotal is exact.
- R15. Every amount is in the one currency given by the rules, held in its smallest unit.
- R16. The total is the sum of the rounded lines and is never recomputed from unrounded values: lines always add up to the total.

Degenerate carts (Q5, delegated):
- R17. An empty cart gives subtotal, discount and total of zero and no fee.
- R18. A line with quantity zero is refused as invalid input; no price is returned.

## 6. Risks and open questions left open

Reserved for later requests, not decided here:
- Money amounts that are negative or overflow.
- Blank or empty identifiers and codes.
- Two operations on the same cart at the same moment.

Other unknowns: the single fee line and the promotion type are placeholders for a real market that is not fixed (market-agnostic stance); the customer-pain evidence is *unverified*. No technical choice is made here.

## 7. Open questions

None remaining for this feature. Q5 (R17, R18) was delegated: confirm or overturn it before relying on it.
