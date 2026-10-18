---
role: product-owner
status: done
reasons: []
---

# Stories: price a cart

Source: PRD `docs/product/prd/price-a-cart.md` (R1..R18), decision log `docs/business/decisions.md`. No glossary exists yet. Two stories, thinnest path first.

## Story 1: price a cart with a delivery fee, no promotion

As the caller (display or order handoff), I give the cart lines, the money rules and a currency, and I receive the full breakdown and an exact total, so that a customer sees every line and the total never surprises them (O1).

Acceptance criteria:
1. The subtotal is the sum over lines of unit price times quantity, exact. (R1, R14)
2. The result exposes every line: subtotal, discount, fee line, total. (R2)
3. Without a code, the discount is zero. (R11)
4. The fee line is the flat delivery fee taken from the rules. (R12, D-10)
5. Total = subtotal - discount + fee, and equals the sum of the lines shown. (R13, R16)
6. All amounts are in the single currency of the rules, held in its smallest unit. (R15, D-13)
7. No amount, rate, threshold or currency is built in; changing one rule parameter changes the result and nothing else. (R4, R6, D-2)
8. The same cart, rules and code always give the same result; the cart is unchanged after pricing. (R3, R5)
9. An empty cart gives subtotal, discount and total of zero and no fee line. (R17, D-24)
10. A cart with a line of quantity zero is refused as invalid input; no price is returned. (R18, D-24)
11. A line holds a unit price and a quantity only; its amount is in the currency of the rules. (R15, D-27)
12. The delivery fee parameter is expressed in the currency's smallest unit; the fee line equals it unchanged. (R12, R14, D-26)
13. The result has named fields in this order: subtotal, discount, fee line, total; the fee line is absent (not zero) for an empty cart. (R2, R17, D-31)
14. A non-empty cart whose subtotal is zero (every unit price 0) is priced normally and still has the fee line. (R12, R17, D-32)

## Story 2: apply one percentage promotion

As the caller, I add an optional promotion code, so that the result shows the discount, or the reason the code did not apply, and the total stays exact.

Depends on story 1.

Acceptance criteria:
1. A valid code applies a percentage off the food subtotal; the rate is a parameter of the rules. (R7, D-8)
2. The discount is subtotal times rate, rounded once, half up, to the smallest unit; the total uses that rounded discount. (R8, R14, R16, D-11)
3. A subtotal equal to the minimum parameter is not "below" it: the promotion applies. (R9)
4. An unknown code gives a result with no discount, the reason stated in the result; pricing succeeds. (R9, D-9)
5. A subtotal below the minimum parameter gives a result with no discount, the reason stated in the result; pricing succeeds. (R9, D-9)
6. When the code is unknown and the subtotal is also below the minimum, the result states one reason only: the unknown code. (R9, D-23)
7. An empty cart with a valid code is a subtotal of zero: with a positive minimum, no discount and the below-minimum reason; with an unknown code, the unknown-code reason. (R9, R17, D-25, D-23)
8. Rules whose rate is below 0 or above 100 percent are rejected by an exception raised when the rules are built, so no cart is priced with them; 0 and 100 percent are valid (0 gives no discount, 100 gives the whole subtotal). (D-22, D-28, D-29)
9. The discount never exceeds the subtotal; the food total after discount is never below zero. (R10)
10. The fee line is identical with and without a promotion; the promotion never discounts the fee, so the total is never below the fee. (R12, R13)
11. A line of quantity zero is refused even when a code is supplied; no price and no discount are returned. (R18, with R9)
12. The reason is one of two values, unknown code or subtotal below minimum, held in one field; the field is empty when the promotion applied or no code was supplied. A valid code whose discount rounds to zero counts as applied: discount zero, no reason. (R9, R11, D-33)
13. The promotion is optional in the rules: rules without one are valid, and any supplied code is then unknown. One promotion has one code, one rate and one minimum. (R7, R9, D-34)
14. A code matches by exact text: case-sensitive, no trimming. (R9, D-34)
15. The rate bounds are checked by the rules, not by the percentage value; the rate is a fraction numerator over 10^scale, scale 0 to 18. (D-22, D-35, D-36)

### Rule pairs that can co-occur

| Pair | Outcome | Where |
|---|---|---|
| Minimum x cap | Below minimum: no discount, cap moot. At or above minimum: discount capped at the subtotal | Story 2 criteria 3, 5, 9 (R9, R10) |
| Rounding x cap | Discount is rounded, then must not exceed the subtotal | Story 2 criteria 2, 9 (R8, R10, R14); the rate is bounded to 0..100 percent (criterion 8, D-22) |
| Rounding x minimum | The minimum compares to the exact subtotal (R14 says it is exact) | Story 2 criterion 3 |
| Rounding x empty cart | Everything is zero, nothing to round | Story 1 criterion 9 (R17) |
| Empty cart x fee | No fee | Story 1 criterion 9 (R17) |
| Empty cart x code | Discount zero, below-minimum reason if the minimum is positive | Story 2 criterion 7 (R17, D-25) |
| Quantity zero x anything (empty line set, code, minimum) | Refused, no price | Story 1 criterion 10, Story 2 criterion 11 (R18) |
| Cap x fee | Fee untouched; total at least the fee | Story 2 criterion 10 (R13) |
| Unknown code x below minimum | Unknown-code reason only | Story 2 criterion 6 (D-23) |
| Rounding x fee | Fee parameter is already in minor units, unchanged | Story 1 criterion 12 (D-26) |

## Open points

None remaining apart from the reserved questions below.

## Reserved, not decided (PRD section 6)

Negative or overflowing amounts; blank or empty identifiers and codes; two operations on one cart at the same moment. No criterion above takes a position on them; a role that meets one asks.
