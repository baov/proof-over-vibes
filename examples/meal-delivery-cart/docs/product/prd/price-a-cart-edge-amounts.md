# PRD: price a cart, edge cases on amounts

Status: ready. Q1 to Q3 answered and read by the human; none delegated. Follows `price-a-cart.md` (R1 to R18 stay true) and settles what its section 6 reserved: "money amounts that are negative or overflow" (D-30). Serves vision outcome O1 and the anti-goal "a total that differs from the amount at order time". Rate scale: D-35, D-36.

## 1. Problem

Facts about the current behavior, from the decision log and the reviews (the code was not read for this PRD):
- A negative quantity, unit price, fee or promotion minimum is accepted and gives a negative total or wrongly rounded values (for example one line of quantity 1 at unit price -500 with a fee of 250 gives a total of -250).
- An amount too large for the money range reaches the caller as a raw arithmetic error that says nothing about the cause.
- The rules accept a rate with a scale of 10 to 18 decimals, but such a rate cannot price ordinary amounts (an intermediate result overflows before the discount is computed).

A caller that shows or confirms a total can show a negative price, a wrong price, or an unreadable failure. That breaks O1.

## 2. Goal and success

Every cart and every rules set either gives a correct result or is refused with a cause the caller can read. Success: no input gives a wrong total without a refusal.

## 3. Users and use

Same caller as `price-a-cart.md`. Main path unchanged: valid cart and valid rules give the breakdown and total.

## 4. Scope

In: amounts of a line (quantity, unit price), of the rules (fee, promotion minimum, rate scale), and amounts too large for the money range.
Out: blank codes and simultaneous operations (see `price-a-cart-edge-codes-and-concurrency.md`); tax, tip, other fee lines.

## 5. Requirements

Independent of the open questions:
- A1. For every cart and rules that were valid before, the result is unchanged (R1 to R18 hold).
- A2. A total that is not the exact result of the rules is never returned: when an amount cannot be represented, no price is returned.
- A3. The refusal for an amount too large names that cause, and can be told apart from the other refusals (quantity zero, rate out of range).
- A4. The refusal covers every amount computed along the way, not only the total: subtotal, discount, fee line, total.
- A5. A refused cart or rules changes nothing and can be priced again after correction.
- A6. Zero stays valid: a unit price of 0 (D-32), a fee of 0, a minimum of 0, a rate of 0 or 100 percent (D-29).

Negative amounts (Q1):
- A7. A line with a negative quantity or a negative unit price is refused as invalid input, like quantity zero (R18); no price is returned.
- A8. Rules with a negative fee or a negative promotion minimum are refused when they are built, like a rate out of range (D-28); no cart is priced with them.
- A9. No input gives a negative total, discount or subtotal.

Too large (Q2):
- A10. When the subtotal, the discount, the fee line or the total cannot be represented in the money range, no price is returned and the caller gets the refusal of A3, named "amount too large".

Rate scale (Q3):
- A11. Every rate the rules accept, at any accepted scale, prices a cart correctly whenever the subtotal, discount, fee line and total are within the money range.
- A12. No rate accepted by the rules is refused as too large merely because of its scale or numerator; only a result beyond the range is (A10).

## 6. Risks and open questions left open

Reserved for the other edge-case request, not decided here: blank or empty codes and identifiers; simultaneous operations on one cart.

Technical unknowns, named not answered, for the architect and orchestrator: how intermediate results are protected from overflow; the exact refusal type; where each check lives; a mutation gap (the default mutators do not touch the exact-arithmetic calls, so only behavior tests guard sums).

## 7. Open questions

None remaining. Q1 (A7 to A9), Q2 (A10), Q3 (A11, A12) were answered and read by the human.
