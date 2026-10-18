---
role: planner
status: done
reasons:
  - "Answered (D-42, D-43, D-44). Was: three caller-visible behaviors that no document decides (section 6, Q1..Q3). The plan below is complete on the recommended options (A); the next round only edits the lines marked 'pending Qn'."
---

# Price a cart, edge cases on amounts (A1..A12)

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress (Q1..Q3 answered: D-42, D-43, D-44)

## 2. Goal

Every cart and every rules set either prices exactly or is refused with a cause the caller can read. Negative quantity, unit price, fee and promotion minimum are refused as invalid input (`IllegalArgumentException`, D-37). An amount beyond the money range (subtotal, discount, fee line, total) gives no price and a distinct refusal `AmountTooLargeException` (D-38). Every rate scale 0 to 18 prices correctly whenever the results fit (D-39). Valid inputs of before give the same results (A1). Acceptance criteria: A1 to A12 of `docs/product/prd/price-a-cart-edge-amounts.md`, nothing else.

## 3. Context

Sources read: brief (with `Carried over`), `architect.md` (done, structure decided), ADR-0001/0002/0003, `docs/technical/invariants.md`, the PRD, decisions D-28..D-41, the code (`domain.money.Money`, `Percentage`, `domain.cart.CartLine`, `Cart`, `domain.rules.PricingRules`, `Promotion`, `domain.pricing.price`, `application.PriceCart`), the 54 existing tests and 35 test-cases, the two earlier plans. No `.plans/FEEDBACK.md`.

**Existing code, as found**
- `Money(minorUnits: Long, currency)`: `plus`, `minus`, `times(Int)` use `Math.*Exact` (raw `ArithmeticException`); `times(Percentage)` computes `Math.multiplyExact(minorUnits, numerator)` then divides half up: it overflows from about 922 EUR at scale 15 and 92 minor units at scale 18 (carried-over major). The half-up test `2 * remainder >= divisor` is wrong for a negative operand.
- `CartLine.init` only refuses quantity zero. `PricingRules.init` refuses a fee or minimum in another currency and a rate outside `0..denominator`. `Percentage` checks only its scale (D-36).
- `domain.pricing.price` computes `subtotal = zero + sum(unitPrice * quantity)` (the `times` is evaluated before the `plus`, so before the currency check of the sum), the discount, then `total = subtotal - discount + feeLine`. This order is kept (see B8).

**Invariants that apply** (run `bash tools/harness/run_all.sh` after each green; the sensitive money zone, `domain.money` and `domain.pricing` and their tests, is touched: a person reads this diff)
- INV-001: `java.math.BigInteger` is JDK; `domain` stays free of any other import. INV-002: rounding stays in `domain.money` (`BigInteger.divideAndRemainder` is not in the rounding set; no `RoundingMode`; no `Math.floorDiv` outside the package). INV-003: `BigInteger` is allowed (only `Double`, `Float`, `BigDecimal` are banned; the architect confirmed, no amendment). INV-004: nothing impure. INV-005: every test below has a test-case and every test-case a test. INV-006: mutation, see section 4 "Proof of the exact calls".

**Decisions applied, not reopened**: ADR-0002 (`Money` is `Long` minor units; nothing wide stored or exposed), ADR-0003 (`AmountTooLargeException` in `domain.money`, subclass of `ArithmeticException`, thrown by `Money` only; `domain.pricing` adds no catch; `PriceCart.price` signature unchanged), architect placement of checks (`CartLine.init` for A7, `PricingRules.init` for A8, `Money` for A10), D-24, D-28, D-29, D-32, D-35, D-36, D-37, D-38, D-39. Another request in flight (`edge-codes-and-concurrency`, D-40/D-41) edits `PricingRules.init` and `domain.pricing.price` too: expect a trivial merge, the two requests are independent.

### What the plan decides from the documents (no question)

- **Order of refusals, negative versus too large.** All refusals of negative input happen at construction (`CartLine(...)`, `PricingRules(...)`), before `price` is called; too large happens only inside `price`. So a negative input always wins: a caller holding an oversized and negative line never reaches pricing. A line that is negative in both quantity and unit price, or a fee that is negative and in another currency, gives the same type (`IllegalArgumentException`); which check fires first is not observable beyond the message (not a contract, not tested).
- **`Long.MIN_VALUE`, `Int.MIN_VALUE`.** A unit price of `Long.MIN_VALUE`, a quantity of `Int.MIN_VALUE`, a fee or a minimum of `Long.MIN_VALUE`: negative, so `IllegalArgumentException` at construction. `Money(Long.MIN_VALUE, c)` itself stays buildable (Money is signed, architect) and `Money.times(Int.MIN_VALUE)` is exact arithmetic with the `Long.MIN_VALUE` boundary (section 4, M3).
- **The caller sees `AmountTooLargeException`** whichever of subtotal, discount, fee line or total cannot be represented, and in every case no `Price` exists (an exception is thrown, there is no partial result). Through pricing the discount cannot be the one that fails (rate at most 100 percent, A9): the discount refusal of A4 is proved on `Money` (M4).
- **Order of lines.** Negatives being refused, every partial sum is non-decreasing, so whether the subtotal fits does not depend on the order of the lines (B11).
- **Boundary.** `Long.MAX_VALUE` is accepted, `Long.MAX_VALUE + 1` is refused, for every amount and operation (section 4).
- **Zero stays valid** (A6): unit price 0, fee 0, minimum 0, rate 0 and 100 percent at every scale.
- **Twice / nothing / invalid / edge / order, for each thing the plan adds or changes**
  - `AmountTooLargeException`: twice = same refusal, nothing changed (B10); nothing = empty cart never raises it, a huge fee on an empty cart has no fee line (B12); invalid = it is not an `IllegalArgumentException`, and an `ArithmeticException` catch still catches it (B9); edge = exactly `Long.MAX_VALUE` fits (B6..B8, M1..M4); order = B11, Q1.
  - `CartLine`: quantity `1` valid, `0`, `-1`, `Int.MIN_VALUE` refused; unit price `0` valid, `-1`, `Long.MIN_VALUE` refused; a huge valid line is built (only pricing refuses it).
  - `PricingRules`: fee `0` valid, `-1`, `Long.MIN_VALUE` refused; minimum `0` valid, `-1`, `Long.MIN_VALUE` refused (only when a promotion exists); a fee or minimum of `Long.MAX_VALUE` is valid rules (pricing decides).
  - `Money.times(Percentage)`: now exact at any scale and any amount; result beyond the range refused; negative operand: refused, D-44.

### Technical choices (no caller can observe; for the reviewer to challenge)

- `domain/money/AmountTooLargeException.kt`: `class AmountTooLargeException(message: String) : ArithmeticException(message)`. The message names the operation and the operands for a human; it is not a contract and no test pins it.
- In `Money`, `plus`, `minus`, `times(Int)` keep `Math.*Exact` and a private helper converts the `ArithmeticException` of that single call into `AmountTooLargeException`; the currency check stays first, so mixed currencies stay `IllegalArgumentException` at the `Money` level.
- `times(Percentage)`: `BigInteger.valueOf(minorUnits) * BigInteger.valueOf(numerator)` (at most 2^63 x 10^18, about 9.2e36, no overflow), `divideAndRemainder(denominator)`, half up with `2 * remainder >= divisor` once, then `longValueExact()` converted to `AmountTooLargeException` when it does not fit. `Math.multiplyHigh` would also do (architect); `BigInteger` is simpler.
- `CartLine.init`: `require(quantity > 0)` replaces `!= 0` and `require(unitPrice.minorUnits >= 0)`. `PricingRules.init`: `require(deliveryFee.minorUnits >= 0)` and, in the promotion block, `require(promotion.minimumSubtotal.minorUnits >= 0)`.
- No `try/catch` and no clamp in `domain.pricing`; the order `subtotal - discount + feeLine` is kept unchanged (it never leaves the range when the total fits).
- Test classes: `EdgeAmountsTest` (new, `application`, boundary `PriceCart` plus the construction calls that refuse) and `MoneyTest` (extended, boundary `Money`, the module API, where an operation cannot be reached through pricing). Fixtures: EUR (2 digits) and JPY (0 digits) as before. Exception tests assert the type, never the message. Large numbers are written as named constants (`max = Long.MAX_VALUE`) in the test.

## 4. Expected behaviors

Test boundary unless stated: `PriceCart.price(cart, rules, code)` in `EdgeAmountsTest`; refusals at construction are observed at the call that raises them. `M` = in `MoneyTest` at the `Money` API (module API, because pricing cannot reach it). Amounts in minor units, EUR; `max = Long.MAX_VALUE = 9223372036854775807`.

**Negative inputs (A7, A8, A9, A6)**

- **B1 negative quantity (A7)**: `CartLine(eur(350), -1)` and `CartLine(eur(350), Int.MIN_VALUE)` raise `IllegalArgumentException`; quantity 1 is accepted; quantity 0 still raises (R18). No price is returned, no cart can hold such a line.
- **B2 negative unit price (A7, A6)**: `CartLine(eur(-1), 1)` and `CartLine(Money(Long.MIN_VALUE, eur), 1)` raise `IllegalArgumentException`; `CartLine(eur(0), 1)` is accepted and a cart of unit price 0 still has the fee line (D-32).
- **B3 negative fee (A8, A6)**: `PricingRules(eur, eur(-1))` and with `Long.MIN_VALUE` raise `IllegalArgumentException`; fee 0 is accepted and gives fee line 0.
- **B4 negative promotion minimum (A8, A6)**: `PricingRules` with a promotion whose minimum is `eur(-1)` or `Long.MIN_VALUE` raises `IllegalArgumentException`; minimum 0 is accepted (valid code applies on any subtotal, also on subtotal 0); rules without a promotion are unaffected.
- **B5 no negative amount (A9)**: for a zero-price cart, a rate of 100 percent on odd and even subtotals, and 99.9 percent on subtotal 1, `subtotal`, `discount`, `feeLine` and `total` are all `>= 0`, `discount <= subtotal` and `total == subtotal - discount + fee`.

**Amount too large (A2, A3, A4, A10)**, always `AmountTooLargeException`, no price returned

- **B6a line beyond the range (A4 subtotal)**: unit price 1317624576693539401 x quantity 7 (= `max`) is accepted, subtotal `max`; unit price 1317624576693539402 x 7 is refused. Quantity boundary: unit price 4294967298 x `Int.MAX_VALUE` (= `max - 1`) is accepted; unit price 4294967299 x `Int.MAX_VALUE` is refused.
- **B6b sum of lines beyond the range (A4 subtotal)**: lines `max - 5` and `5` give subtotal `max`; lines `max - 5` and `6` are refused (each line fits alone).
- **B7 total beyond the range with a subtotal that fits (A4 fee line / total)**: rate none. Subtotal `max - 250` + fee 250 gives total `max`; fee 251 is refused. The same cart with fee 0 is priced (the subtotal alone is not the problem). A cart of one line at unit price 0 with fee `max` gives total `max`; one line at unit price 1 with fee `max` is refused.
- **B8 a total that fits is not refused because of an intermediate (A10, A12)**: subtotal `max` (lines as in B6a), rate 100 percent (`Percentage(1, 0)` and `Percentage(10^18, 18)`), fee 1000: `max + 1000` does not fit but the result does: discount `max`, total 1000, accepted. Discount that fits while the sum does not: subtotal 9000000000000000000, rate 10 percent: discount 900000000000000000, `subtotal - discount` = 8100000000000000000; fee 1123372036854775807 gives total `max` (accepted), fee 1123372036854775808 is refused (the fee line is the amount that pushes the total out).
- **B9 the refusal is its own kind (A3)**: the thrown exception is an `AmountTooLargeException`, an `ArithmeticException`, and not an `IllegalArgumentException`; quantity zero and a rate out of range still raise `IllegalArgumentException` and not `AmountTooLargeException`.
- **B10 a refused pricing changes nothing (A5)**: pricing an oversized cart twice refuses twice; `cart.lines` and the rules are equal to copies taken before; the same rules then price a corrected cart correctly, equal to a fresh result; the same cart with smaller rules (fee 0) is priced. Same for rules: the rules refused at construction (`fee -1`) leave a corrected `PricingRules` buildable and usable.
- **B11 order of lines (A2)**: `[max - 5, 6]` and `[6, max - 5]` are both refused; `[max - 5, 5]` and `[5, max - 5]` both give subtotal `max`.
- **B12 empty cart (A6, R17)**: fee `max` on an empty cart gives zeros, no fee line, total 0 (nothing is refused).
- **B13 the code never hides it (A10)**: an unknown code, a valid code below the minimum, and a valid code, each with a total beyond the range, are refused with `AmountTooLargeException` (no price carrying a reason).
- **B14 a refused currency is refused before amounts (D-42)**: a cart with a line in JPY priced with EUR rules raises `IllegalArgumentException`, also when that line, or an earlier line, holds an amount that would be too large.

**Rate scale (A11, A12)**, boundary `PriceCart`

- **B15 10 percent at every scale**: for every scale 1..18 the rate `Percentage(10^(s-1), s)` and subtotals 100, 100000 (above the old limit at 15) and 100000000 give the same discount and the same whole `Price` as `Percentage(10, 2)`; subtotal 9000000000000000000 gives discount 900000000000000000 at every scale. Scale 0 holds only 0 and 100 percent: `Percentage(0, 0)` gives discount 0, `Percentage(1, 0)` gives the subtotal.
- **B16 half up at every scale**: for every scale 1..18, rate `Percentage(5, s)` (5 x 10^-s): subtotal `10^(s-1)` gives exactly half a unit, discount 1; subtotal `10^(s-1) - 1` gives discount 0 (for s = 1 subtotal 0 gives 0). One rounding on the whole sum, as before.
- **B17 the largest subtotal at any rate (A12)**: subtotal `max` with 10 percent gives 922337203685477581 (…580.7 rounds up) and total `max - 922337203685477581`; 50 percent gives 4611686018427387904 (…903.5 rounds up); 100 percent at scales 0, 1, 9, 18 gives `max`; `Percentage(10^18 - 1, 18)` gives discount 9223372036854775798 and total 9; the same at fee 0 for every scale 1..18 with the 10 percent form.
- **B18 rate bounds at the widest scale (A12)**: rules accept `Percentage(10^18, 18)` (100 percent) and `Percentage(0, 18)`; they refuse `Percentage(10^18 + 1, 18)`, `Percentage(-1, 18)` and `Percentage(Long.MAX_VALUE, 18)` with `IllegalArgumentException`: a large numerator is never "too large", it is out of range.

**Money API (M)**, `MoneyTest`; each `Math.*Exact` call and each narrowing is pinned by a pair of results on either side of the range

- **M1 plus**: `max + 0` and `(max - 1) + 1` give `max`; `max + 1` and `(max/2 + 1) + (max/2 + 1)` raise `AmountTooLargeException`; `Long.MIN_VALUE + 0` fits, `Long.MIN_VALUE + (-1)` raises; `Money(max, eur) + Money(1, jpy)` raises `IllegalArgumentException` (currency check first).
- **M2 minus**: `Long.MIN_VALUE - 0` and `(-1) - max` (= `Long.MIN_VALUE`) fit; `(-2) - max`, `0 - Long.MIN_VALUE` and `max - (-1)` raise `AmountTooLargeException`; `max - max` is 0.
- **M3 times(Int)**: `max x 1` fits, `max x 2` raises; `2^32 x Int.MIN_VALUE` (= `Long.MIN_VALUE`) fits, `(2^32 + 1) x Int.MIN_VALUE` raises; `Long.MIN_VALUE x -1` raises; `0 x Int.MAX_VALUE` is 0.
- **M4 times(Percentage) range (A4 discount)**: `max x Percentage(1, 0)` fits (`max`); `max x Percentage(2, 0)` raises; `4611686018427387903 x Percentage(2, 0)` fits (`max - 1`), `4611686018427387904 x Percentage(2, 0)` raises; `1 x Percentage(Long.MAX_VALUE, 0)` fits, `2 x Percentage(Long.MAX_VALUE, 0)` raises; `max x Percentage(Long.MAX_VALUE, 18)` raises (the wide product itself did not overflow); `max x Percentage(10^18, 18)` fits (`max`).
- **M5 times(Percentage) rounds before it narrows**: exact result `max - 0.5` (`Money(252785) x Percentage(364870227143809, 1)`) rounds half up to `max` and fits; exact result `max + 0.5` (`Money(33502085) x Percentage(2753074036095, 1)`) rounds to `max + 1` and raises.
- **M6 times(Percentage) on a negative operand (D-44)**: a negative amount or a negative numerator raises `IllegalArgumentException`; zero amount and zero numerator are accepted.

### Proof that each exact call is tested by a behavior (PIT does not mutate `Math.*Exact` or `longValueExact`)

| Call | Behaviors that fail if it becomes the plain operator | How it is checked |
|---|---|---|
| `Math.addExact` in `plus` | M1 (`max + 1`, `Long.MIN_VALUE + -1`), B6b, B7 | manual mutation, below |
| `Math.subtractExact` in `minus` | M2 (`0 - Long.MIN_VALUE`, `(-2) - max`, `max - -1`) | manual mutation |
| `Math.multiplyExact` in `times(Int)` | M3, B6a | manual mutation |
| `longValueExact` (narrowing) in `times(Percentage)` | M4, M5 | manual mutation |
| the conversion to `AmountTooLargeException` (catch) | B9, B6a..B8, M1..M5 assert the type, not `ArithmeticException` | manual mutation (replace by a rethrow of the raw exception) |

The exact boundaries (`max` accepted, `max + 1` refused) are what separate "exact call" from "plain operator" (a wrapped value `Long.MIN_VALUE` is returned instead of a refusal). The `>= 0` and `> 0` guards and the half-up comparison are ordinary mutants: PIT covers them (zero accepted / minus one refused / exactly half tests).

## 5. Steps

TDD, one behavior at a time (red, green, refactor); after each green `bash tools/harness/run_all.sh`; Maven: `tools/harness/_maven.sh -o test`; each test-case file is created together with its test (front-matter `feature: price-a-cart`, `source: PRD A.., D-37..D-39`, `status: covered`, `automated_test` exactly as the test name). The 54 existing tests stay unchanged and green at every step (A1); if one must change, that is a deviation.

- [ ] Step 1: negative inputs. Create `src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt` with B1, B2 (red), then `CartLine.init` (`quantity > 0`, `unitPrice.minorUnits >= 0`); B3, B4 (red), then `PricingRules.init`; B5. Test-cases: `negative-quantity-refused`, `negative-unit-price-refused`, `negative-fee-refused`, `negative-promotion-minimum-refused`, `no-amount-of-a-price-is-negative`. Edit the doc comment of `CartLine` (a line of quantity zero or less cannot exist).
- [ ] Step 2: the refusal type. Add `domain/money/AmountTooLargeException.kt`. Write M1, M2, M3 in `MoneyTest.kt` (red: raw `ArithmeticException` is not an `AmountTooLargeException`), then convert in `Money.plus`, `minus`, `times(Int)`. Then B6a, B6b, B7, B9 in `EdgeAmountsTest` (red for B9 type, green after Step 2). Test-cases: `money-addition-boundary`, `money-subtraction-boundary`, `money-multiplication-by-quantity-boundary`, `subtotal-line-beyond-the-range-refused`, `subtotal-sum-beyond-the-range-refused`, `total-beyond-the-range-refused`, `amount-too-large-is-its-own-refusal`.
- [ ] Step 3: the wide product. Write B15, B16 first (red at scales 15 to 18), then B17, B18, M4, M5 (red); change `Money.times(Percentage)` to the `BigInteger` product, half up once, narrowing converted to `AmountTooLargeException`. Test-cases: `ten-percent-prices-the-same-at-every-scale`, `half-up-at-every-scale`, `largest-subtotal-is-discounted-exactly`, `rate-bounds-hold-at-the-widest-scale`, `money-rate-range-boundary`, `money-rate-rounds-before-narrowing`. Run `run_all.sh`: INV-002 and INV-003 must still pass with `BigInteger` (if INV-001..004 reject it, that is a deviation, not a workaround).
- [ ] Step 4: total, order and idempotence. B8 (the order `subtotal - discount + fee` is kept: a test that would fail if the total were computed as `subtotal + fee - discount`), B10, B11, B12, B13. Test-cases: `total-that-fits-after-the-discount-is-accepted`, `refused-pricing-changes-nothing`, `order-of-lines-does-not-change-the-refusal`, `empty-cart-ignores-a-huge-fee`, `code-does-not-hide-amount-too-large`.
- [ ] Step 5: answers applied (D-42: pre-pass in `domain.pricing.price` requiring each line currency to equal the rules currency, before any amount; D-44: `Money.times(Percentage)` requires amount and numerator >= 0). Q1 -> B14 and its test-case `currency-refused-before-amounts` (and `Pricing.kt` as the answer says); Q3 -> M6 and test-case `money-rate-of-a-negative-operand` (and `Money.times(Percentage)`); Q2 -> only the exception docs. 
- [ ] Step 6: manual mutation of the exact calls (section 4 table). One at a time, replace `Math.addExact(a, b)` by `a + b`, `Math.subtractExact` by `-`, `Math.multiplyExact` by `*`, `longValueExact()` by `toLong()`, the conversion by a rethrow; run `MoneyTest` and `EdgeAmountsTest`; each replacement must make the behaviors named in the table fail. Revert each. Record the five outcomes in section 9. Also temporarily compute the total as `subtotal + fee - discount`: B8 must fail.
- [ ] Step 7: closing. `tools/harness/_maven.sh -o test`; `bash tools/harness/run_all.sh` (INV-001..005; `check_test_coverage.py`: 0 pending, 0 broken, 0 orphan); `bash tools/harness/run_mutation.sh --scope diff` (record the score; survivors on `Money`/`CartLine`/`PricingRules` are real gaps to fix by a behavior, not by a mutant-killing test; the known survivor `Percentage.getScale` stays carried over); run the new tests through the "wrong direction signals" of `behavior-driven-testing`.

## 6. Risks & edge cases

- Sensitive zone (money): `Money.times(Percentage)` is rewritten. The half-up test `2 * remainder >= divisor` and the `longValueExact` narrowing are the lines that decide a price; B16 (exactly half at every scale), M5 (half at the range limit) protect them.
- Hidden overflow in another place: `Percentage.denominator` is `10^scale` up to `10^18`, fits a `Long`; the wide product is at most 2^63 x 10^18 < 2^127, no overflow. `Money.times(Int)` widens the `Int` to `Long` first (`Int.MIN_VALUE` is exact).
- Compatibility (A1): a caller catching `ArithmeticException` still catches the new type; no signature changes in `PriceCart`, `Price`, `CartLine`, `PricingRules`.
- A caller that built a line with negative price before now gets an `IllegalArgumentException` at the line: that is the requested behavior (D-37), not a regression.
- Merge with the other edge-case request on `PricingRules.init` and `domain.pricing.price` (small).
- `Math.*Exact`, `longValueExact` and the catch are invisible to PIT: covered by Step 6, recorded, not by a threshold.

### Questions to the product owner (round 1: all answered, `answers.md`, D-42 = Q1 A, D-43 = Q2 A, D-44 = Q3 A; nothing consumer-visible remains open)

**Q1. A cart with a line in another currency than the rules AND an amount that would be too large: which refusal does the caller get?** Today it depends on an accident of evaluation: an oversized line is refused as too large, an oversized later line in another currency as invalid currency.
- A (recommended): the currency refusal (`IllegalArgumentException`) always wins, whatever the amounts: invalid input is refused before any amount is computed.
- B: whichever problem the pricing meets first, line by line (an oversized line before the foreign one gives "too large").
- C: other / let me explain.

**Q2. What does the caller learn from "amount too large"?** A3 says the refusal names its cause; the PRD does not say which amount.
- A (recommended): the type alone: `AmountTooLargeException` (in `domain.money`, an `ArithmeticException`); the message is for humans, not a contract, and does not say which amount (subtotal, discount, fee line or total).
- B: the type plus a field telling which amount failed (subtotal, fee line, total). It needs pricing to catch and re-throw, which the architect excluded (ADR-0003): ask the architect again.
- C: other / let me explain.

**Q3. What does `Money.times(rate)` do with a negative amount or a negative rate numerator?** Pricing never reaches it (A7..A9 refuse negatives first), but `Money` and `Percentage` are public and both can hold a negative; today the rounding is wrong for them (carried-over major: "negative subtotals round wrongly").
- A (recommended): refused as invalid input (`IllegalArgumentException`); zero is fine. No wrong value can ever come out of it.
- B: defined: half up toward plus infinity for every sign (-0.5 gives 0, -1.5 gives -1).
- C: defined: half away from zero (-0.5 gives -1).
- D: left undecided and untested (the wrong rounding for negatives stays).

Not questions: the message text of any refusal (not a contract, untested); the name `AmountTooLargeException` and its package (ADR-0003, architect); `Percentage(10, 2) != Percentage(100, 3)` (no requirement A needs it: B15 compares prices, not rates).

## 7. Out of scope

- Blank or empty codes and simultaneous operations (`edge-codes-and-concurrency`).
- Equality of equivalent `Percentage` values; the survivor `Percentage.getScale`.
- A result type replacing the exception, an amount stored wide, a wider money type, a new currency or tax rule, any new fee line, any message wording contract.
- A catch, a clamp or a pre-check of ranges in `domain.pricing` (the architect placed the checks in `Money`, `CartLine`, `PricingRules`); the only exception is Q1 A if answered so (a currency pre-check, no range check).
- Any `Double`, `Float`, `BigDecimal`; any rounding outside `domain.money`.

## 8. Deviations

(empty)

## 9. Self-review

(empty)

## 10. Follow-up actions

(empty)
