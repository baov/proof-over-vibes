---
role: planner
status: done
reasons: []
---


# Price a cart, story 2: apply one percentage promotion

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress (Q1..Q3 answered: D-33, D-34, D-35; conflict settled: D-36)

## 2. Goal

The caller adds an optional promotion code to the pricing call. A valid code takes a rate (a parameter of the rules) off the food subtotal, rounded once, half up, to the smallest unit; otherwise the result carries no discount and the typed reason. The fee is never discounted and the total stays exact. Acceptance criteria: Story 2 of `../stories.md` (1..11), nothing else. Story 1 callers and tests keep working unchanged.

## 3. Context

Sources read: brief (story 2, "Carried over"), `../stories.md`, `../architect.md` (front-matter and ADRs final), ADR-0001/0002, `invariants.md`, decision log D-1..D-32, PRD, the existing code and tests, the 15 story 1 test-cases, the story 1 archive (`plan.md`, `answers.md`), the harness. No `.plans/FEEDBACK.md`.

**Existing code** (base package `io.example.mealcart`): `Money(minorUnits: Long, currency)` with `plus`, `minus`, `times(Int)`, `zero`; `CartLine`, `Cart`; `PricingRules(currency, deliveryFee)`; `Price(subtotal, discount, feeLine, total)`; top-level `price(cart, rules)` in `domain.pricing`; `PriceCart.price(cart, rules)`. The discount is hard-coded to zero; nothing rounds; no `Percentage` exists. Tests: `PriceCartTest` (15 tests, all through `PriceCart`).

**Invariants that apply** (run `bash tools/harness/run_all.sh` after each green):
- INV-001 dependency rule: new types stay in `domain`, imports stdlib only.
- INV-002 only `domain.money` rounds: the half-up function and the rate application live in `domain.money`; `domain.pricing` calls them and never divides.
- INV-003 no `Double`, `Float`, `BigDecimal`: the rate is an integer numerator over a power of ten.
- INV-004 purity. INV-005 each test-case points at an existing test, each test class has a test-case. INV-006 mutation (`--scope diff` at closing; no threshold).
- Sensitive zone (money): `domain.money` and `domain.pricing` and their tests change here (rounding, discount): a person reads this diff.

**Decisions applied, not reopened**: hexagonal light; `Money` in `Long` minor units; exact decimal `Percentage` (ADR-0002); one rounding point; pricing is a pure function over immutable inputs; rules validated at construction by `require` (`IllegalArgumentException`) so no cart is priced with invalid rules (D-22, D-28, D-29); a `CartLine` of quantity zero cannot exist (D-24); D-9, D-10, D-23, D-25, D-26, D-31, D-32.

**Conflict between documents (settled by D-36)**: the architect note says `Percentage` guards "non-negative numerator", while Story 2 criterion 8 and D-28 say a rate below 0 is rejected *when the rules are built*. A `Percentage` that refuses a negative numerator would raise earlier, at the `Percentage` call, never at the rules. The plan follows the stories and the human decision (D-22, D-28): `Percentage` validates only its scale and may hold a negative numerator; `PricingRules` rejects any rate outside 0..100 percent. The architect note is not edited. 

**Extension points left by story 1** (used, not changed): a trailing property on `Price`; a trailing optional parameter on `PriceCart.price` and `price`; a trailing optional parameter on `PricingRules`. Story 1 tests (destructuring of four components, `copy`, two-argument calls, two-argument rules) must compile and pass unchanged.

### Answers applied (D-33 Q1, D-34 Q2, D-35 Q3; Story 2 criteria 12 to 15)

- Q1 A: `Price` gains a trailing `promotionNotApplied: PromotionNotApplied?`, a closed enum `UNKNOWN_CODE`, `SUBTOTAL_BELOW_MINIMUM`; `null` when the promotion applied, when no code was supplied. A valid code whose discount rounds to zero (including a 0 percent rate, or an empty cart with a zero minimum) is "applied": discount zero, reason `null`.
- Q2 A: `PricingRules(currency, deliveryFee, promotion: Promotion? = null)`, `Promotion(code: String, rate: Percentage, minimumSubtotal: Money)`; one code per rules, matched by exact string equality (case-sensitive, no trimming); rules with no promotion know no code, so any supplied code is unknown.
- Q3 A: `Percentage(numerator: Long, scale: Int)` is `numerator / 10^scale` as a fraction of the amount (`Percentage(10, 2)` = 10 percent, `Percentage(125, 3)` = 12.5 percent, `Percentage(1, 0)` = 100 percent), scale 0..18 (10^scale fits a `Long`), otherwise `IllegalArgumentException`.

### Technical choices (no caller can observe; for the reviewer to challenge)

- `Percentage` lives in `domain.money` next to the rounding function (ADR-0001: only that package rounds). `Money.times(rate: Percentage)` returns the half-up rounded amount; the private rounding is `quotient + (if 2 * remainder >= divisor then 1 else 0)` on non-negative operands, with `Math.multiplyExact` for `minorUnits * numerator`. Negative operands are not given a rounding rule (reserved, D-30).
- `Promotion` is a plain data holder with no `init`; all validation (rate within 0..100 percent, minimum in the currency of the rules) sits in `PricingRules.init`, so the exception is raised at the `PricingRules(...)` call, as the stories say.
- The cap (criterion 9) needs no `min(discount, subtotal)`: with a rate at most 100 percent and an integer subtotal, the half-up result cannot exceed the subtotal. A defensive clamp would be an unkillable mutant. The behavior is protected by tests at 100 percent and just below it.
- The minimum is compared with `Money` ordering (`compareTo` on same-currency minor units, added to `Money` with the same-currency guard); the subtotal compared is the exact sum.
- Decision order in `domain.pricing`: no code, then unknown code (also when the rules hold no promotion), then below minimum, then apply. That order is D-23 (unknown code wins).
- Test classes: `ApplyPromotionTest` (boundary `PriceCart`, plus the construction of `PricingRules` and `Percentage`) and `MoneyTest` (boundary `Money`, the module API, for the subtraction guard). Fixtures as in story 1: EUR (2 digits) and JPY (0 digits). Exception tests assert the type, not the message. The message of the out-of-range rate names the rate and the bounds (human reading only); it is not a contract and no test pins it.

## 4. Expected behaviors

Test boundary unless stated: `PriceCart.price(cart, rules, code)` in `ApplyPromotionTest`; refusals are observed at the construction call that raises them. AC = Story 2 criterion. Amounts in minor units; rules EUR with fee 250 unless stated; promotion "WELCOME10", rate 10 percent, minimum 1000.

- **B1 valid code applies the rate (AC1)**: given subtotal 2000 and code "WELCOME10", then discount 200, reason absent, total 2050 (2000 - 200 + 250).
- **B2 rounding half up, once (AC2)**: rate 5 percent (`Percentage(5, 2)`), minimum 0: subtotal 1009 -> discount 50 (50.45); 1010 -> 51 (exactly half, up); 1011 -> 51 (50.55); a fractional rate 12.5 percent (`Percentage(125, 3)`) on 1001 -> 125 (125.125); in JPY, 5 percent on 1010 -> 51 (smallest unit is the yen). The total uses the rounded discount: 1010 + fee -> total = 1010 - 51 + fee. Rounding is applied once to subtotal x rate: with lines (333 x 1) three times at 10 percent, the discount is round(99.9) = 100, not 3 x round(33.3) = 99.
- **B3 minimum reached (AC3)**: minimum 1000, subtotal 999 -> below minimum; 1000 -> applies (discount 100); 1001 -> applies (discount 100, 100.1).
- **B4 unknown code (AC4)**: code "OTHER" -> discount zero, reason `UNKNOWN_CODE`, pricing succeeds, fee line present, total = subtotal + fee.
- **B5 below minimum (AC5)**: subtotal 999, valid code -> discount zero, reason `SUBTOTAL_BELOW_MINIMUM`, total = subtotal + fee.
- **B6 unknown code wins (AC6, D-23)**: unknown code and subtotal below minimum -> reason `UNKNOWN_CODE` only.
- **B7 empty cart with a code (AC7)**: positive minimum + valid code -> zeros, no fee line, reason `SUBTOTAL_BELOW_MINIMUM`; unknown code -> reason `UNKNOWN_CODE`; minimum 0 + valid code -> zeros, no fee line, no reason (Q1 A).
- **B8 rate bounds (AC8, D-22, D-28, D-29)**: `PricingRules` with a rate above 100 percent (`Percentage(101, 2)`, `Percentage(1001, 3)`) or below 0 (`Percentage(-1, 2)`) -> `IllegalArgumentException` at the `PricingRules(...)` call, so no price is returned; 0 percent and 100 percent (`Percentage(100, 2)` and `Percentage(1, 0)`) are accepted: 0 gives discount zero, 100 gives the whole subtotal.
- **B9 cap (AC9)**: at 100 percent the discount equals the subtotal (odd and even subtotals, 1 and 1001), the food total after discount is zero and the total equals the fee; at 99.9 percent (`Percentage(999, 3)`) on subtotal 1 the discount is 1, not 2 and not above the subtotal.
- **B10 fee untouched (AC10)**: the same cart and rules priced with and without the code give the same fee line; at 100 percent the total equals the fee, never below it.
- **B11 quantity zero with a code (AC11)**: `CartLine(price, 0)` raises `IllegalArgumentException` before any code is seen; the call `PriceCart.price(Cart(listOf(CartLine(eur(350), 0))), rules, "WELCOME10")` never produces a price.

Rules-of-the-plan edge cases ('twice / nothing / invalid / edge / order'):
- **E1 no code supplied (R11)**: rules hold a promotion, no code -> discount zero, reason absent.
- **E2 code with rules that hold no promotion**: any code -> discount zero, reason `UNKNOWN_CODE`.
- **E3 exact match (Q2 A)**: "welcome10" and " WELCOME10" (different case, a space) are unknown codes. A blank or empty code is NOT tested and NOT guarded (reserved by PRD section 6; with exact matching it is simply unknown unless the rules were built with that same blank text; no decision here).
- **E4 same input twice (R3, R5)**: pricing twice with the same cart, rules and code gives equal results (the discount does not accumulate); the cart and the rules are unchanged; the order of the lines does not change the discount.
- **E5 promotion minimum in another currency than the rules**: `PricingRules` raises `IllegalArgumentException` at construction (R15, architect).
- **E6 scale out of 0..18**: `Percentage(5, -1)` and `Percentage(5, 19)` raise `IllegalArgumentException`.
- **E7 non-zero discount protects the sums (carried-over minors)**: a case with a non-zero discount AND a non-zero fee and several lines asserts every field: subtotal, discount, fee line, total as exact numbers (subtotal 2150 with lines 350 x 2 and 1450 x 1, 10 percent, fee 250: discount 215, total 2185). Differently shaped values kill `subtractExact` -> `addExact`, `minus` ignoring its operand, `total = subtotal + discount`, and any sum of discount into the wrong place. `Money` module API: subtracting amounts in two currencies is refused (the guard in `minus` is unreachable through `PriceCart`); subtraction is exact.
- **E8 discount that rounds to zero (Q1 A)**: 1 percent on subtotal 10 (0.1) -> discount zero, reason absent, total = subtotal + fee.
- **E9 reserved, no rule, no test, no guard**: negative or overflowing amounts (the two carried-over majors; D-30): `subtotal x numerator` overflowing is a raw `ArithmeticException` like any other overflow; a negative subtotal's rounding is undefined. Blank or empty codes; two operations on one cart.

**Business test-cases** (`docs/business/test-cases/price-a-cart/<slug>.md`, created WITH the test, front-matter and layout as story 1, `status: covered`, priority high, medium for E-cases):

| Slug | Behavior | Test (class: `ApplyPromotionTest` unless noted; name verbatim in `automated_test`) | source |
|---|---|---|---|
| valid-code-takes-the-rate-off | B1 | `a valid code takes the rate off the subtotal` | R7, D-8; c.1 |
| discount-rounds-half-up-once | B2 | `the discount is rounded once, half up, to the smallest unit` | R8, R14, D-11; c.2 |
| minimum-reached-promotion-applies | B3 | `a subtotal equal to the minimum still gets the promotion` | R9; c.3 |
| unknown-code-gives-no-discount | B4, E2 | `an unknown code gives no discount and says why` | R9, D-9; c.4 |
| below-minimum-gives-no-discount | B5 | `a subtotal below the minimum gives no discount and says why` | R9, D-9; c.5 |
| unknown-code-wins-over-minimum | B6 | `an unknown code is the only reason when the subtotal is also below the minimum` | R9, D-23; c.6 |
| empty-cart-with-a-code | B7 | `an empty cart with a code is a subtotal of zero` | R9, R17, D-25, D-23; c.7 |
| rate-outside-zero-to-hundred-refused | B8, E6 | `rules with a rate below 0 or above 100 percent are refused` | D-22, D-28; c.8 |
| rate-bounds-are-valid | B8 | `rates of 0 and 100 percent are valid` | D-29; c.8 |
| discount-never-exceeds-the-subtotal | B9 | `the discount never exceeds the subtotal` | R10; c.9 |
| promotion-never-discounts-the-fee | B10 | `the fee line is the same with and without a promotion` | R12, R13, D-10; c.10 |
| quantity-zero-refused-with-a-code | B11 | `a line of quantity zero is refused even with a code` | R18; c.11 |
| no-code-no-discount-with-a-promotion | E1 | `without a code the discount is zero even when the rules hold a promotion` | R11 |
| code-matches-exactly | E3 | `a code matches only the exact configured text` | R9; Q2 |
| same-code-same-result | E4 | `pricing with the same code twice gives the same result` | R3, R5 |
| promotion-minimum-in-another-currency-refused | E5 | `rules with a promotion minimum in another currency are refused` | R15; architect.md |
| scale-outside-range-refused | E6 | `a rate with a scale outside 0 to 18 is refused` | ADR-0002; Q3 |
| total-adds-up-with-a-discount | E7 | `the total is subtotal minus the rounded discount plus the fee` | R13, R16 |
| discount-rounding-to-zero-is-applied | E8 | `a discount that rounds to zero is applied with no reason` | R8, R14; Q1 |
| money-subtraction-refuses-mixed-currencies | E7 | `MoneyTest.kt::subtracting amounts in two currencies is refused` (`src/test/kotlin/io/example/mealcart/domain/money/MoneyTest.kt`) | ADR-0002 |

Existing test-case `no-discount-without-promotion` is edited (Given: "no code is supplied"), its test `the discount is zero` unchanged. Each test name must appear in its file exactly as written.

## 5. Steps

TDD, one behavior at a time (red, green, refactor); `bash tools/harness/run_all.sh` after each green; each test-case file created with its test; Maven: `tools/harness/_maven.sh -o test`. Story 1 tests stay green at every step.

- [ ] Step 1: Create `src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt` with B1 (red). Add `domain/money/Percentage.kt` (`data class Percentage(numerator: Long, scale: Int)`, `require(scale in 0..18)`), `Money.times(rate: Percentage)` with the private half-up rounding and `Money.compareTo`, `domain/rules/Promotion.kt`, `PricingRules.promotion: Promotion? = null`, `domain/result/PromotionNotApplied.kt`, `Price.promotionNotApplied: PromotionNotApplied?` (trailing), the `code: String? = null` parameter on `domain.pricing.price` and `PriceCart.price`, only as far as B1 needs. Update every `Price(...)` call (pricing only) and check story 1 tests compile unchanged. Test-case `valid-code-takes-the-rate-off`.
- [ ] Step 2: B2: below half, exactly half, above half, fractional rate, JPY, round-once-on-the-sum. Test-case `discount-rounds-half-up-once`. Check by temporary mutation (`>=` -> `>`) that the exact-half test fails.
- [ ] Step 3: E7 + total with a discount: exact numbers for all four fields, several lines, non-zero fee; `MoneyTest` for `minus`. Test-cases `total-adds-up-with-a-discount`, `money-subtraction-refuses-mixed-currencies`. Check by temporary mutation that `minus` -> `plus`, ignoring its operand, and `total = subtotal + discount` each make a test fail.
- [ ] Step 4: B4 + E2 (unknown code, reason `UNKNOWN_CODE`; rules without promotion), then B5 (below minimum), then B3 (equal to the minimum), then B6 (order of the checks). Test-cases `unknown-code-gives-no-discount`, `below-minimum-gives-no-discount`, `minimum-reached-promotion-applies`, `unknown-code-wins-over-minimum`.
- [ ] Step 5: B7 + E1 + E8: empty cart with a code, no code, discount that rounds to zero. Test-cases `empty-cart-with-a-code`, `no-code-no-discount-with-a-promotion`, `discount-rounding-to-zero-is-applied`; edit `no-discount-without-promotion`.
- [ ] Step 6: B8 + E5 + E6: `PricingRules.init` `require`s the rate within `0..10^scale` of numerator and the minimum in the rules' currency; scale guard already in `Percentage`. Test-cases `rate-outside-zero-to-hundred-refused`, `rate-bounds-are-valid`, `promotion-minimum-in-another-currency-refused`, `scale-outside-range-refused`.
- [ ] Step 7: B9 + B10: cap at 100 and 99.9 percent, fee untouched. Test-cases `discount-never-exceeds-the-subtotal`, `promotion-never-discounts-the-fee`. Do not add a `min()` clamp; if a test shows one is needed, that is a deviation.
- [ ] Step 8: B11 + E3 + E4: quantity zero with a code, exact match, same input twice and cart/rules unchanged. Test-cases `quantity-zero-refused-with-a-code`, `code-matches-exactly`, `same-code-same-result`.
- [ ] Step 9: closing: `tools/harness/_maven.sh -o test`; `bash tools/harness/run_all.sh` (INV-001..005, `check_test_coverage.py`: 0 pending, 0 broken, 0 orphan); `bash tools/harness/run_mutation.sh --scope diff` (record the score; the rounding and `minus` mutants must be killed by behavior tests, no mutant-killing test); run the new tests through the "wrong direction signals" of `behavior-driven-testing`. Update the story 1 survivor note in section 9.

## 6. Risks & edge cases

- Sensitive zone: rounding, discount, the sums; wrong half-up or wrong `minus` is a wrong price. A person reads the diff (Reviewer escalation).
- Rounding: `2 * remainder >= divisor` is the only line deciding "half up"; the exactly-half test (1010 at 5 percent) is the one that protects it. Operand sign: only non-negative operands are meaningful (rate validated, subtotal negative is reserved).
- `Math.*Exact` is not mutated by PIT's default mutators: only the behavior tests of step 3 protect the sums.
- Story 1 compatibility: defaults on the three trailing parameters; `Price` gains a fifth component, so destructuring of four components and `copy` in story 1 tests still compile. If a story 1 test must change, that is a deviation.
- RESERVED, not decided, for the later edge-case request: (1) negative quantity, unit price and fee accepted and giving a negative total; (2) overflow reaching the caller as a raw `ArithmeticException` (this story adds one more place where it can occur: `subtotal x numerator`, with the same status). No test, no guard, no test-case in this story. If the plan finds it must touch them, it asks.
- Reserved too: blank or empty codes (E3 only fixes that matching is exact), two operations on one cart.
- Carried-over minors: handled by step 3 (non-zero discount tests, `Money.minus` guard tested on the `Money` API); the default-mutator limit on `Math.*Exact` is noted above.

### Questions to the product owner (round 1: all answered, `answers.md`, D-33..D-36; nothing consumer-visible remains open)

Each is a behavior a caller sees; no document decides it. Recommended option first.

**Q1. What does the result say when the promotion did not apply, and in the two quiet cases?** The architect left the shape to this plan.
- A (recommended): a closed set of two reasons, `UNKNOWN_CODE` and `SUBTOTAL_BELOW_MINIMUM`, in one field that is empty when the promotion applied or when no code was supplied. A valid code whose discount rounds to zero (0 percent rate, 1 percent of 10, an empty cart with a zero minimum) is applied: discount zero, no reason.
- B: as A, plus a third reason for "valid code but the discount is zero".
- C: the field always says one of: no code supplied, applied, or one of the two reasons (never empty).

**Q2. What is the promotion part of the rules, and how is a code matched?** (blank or empty codes stay reserved.)
- A (recommended): optional (rules without a promotion are still valid, and any supplied code is then unknown); one promotion with one code, one rate and one minimum; the code matches only by exact text (case-sensitive, no trimming).
- B: as A, but the match ignores letter case.
- C: as A, but the promotion holds several codes sharing one rate and one minimum (the architect wrote "code(s)").

**Q3. What is the rate, as a type the caller builds?**
- A (recommended): `Percentage(numerator, scale)` = numerator over 10 to the scale as a fraction of the amount: `Percentage(10, 2)` is 10 percent, `Percentage(125, 3)` is 12.5 percent, `Percentage(1, 0)` is 100 percent; scale from 0 to 18, otherwise refused; a negative numerator can be built and is refused by the rules (D-28).
- B: `Percentage(numerator, scale)` read as a number of percent: `Percentage(10, 0)` is 10 percent, `Percentage(125, 1)` is 12.5 percent, `Percentage(100, 0)` is 100 percent; same scale limits and same refusal by the rules.
- C: whole percents only (0..100, no decimals): a coarser rate type, with no fractional rate possible.

Not a question: the message text of the out-of-range rate refusal (plan: names the rate and the bounds, untested).

## 7. Out of scope

- Negative or overflowing amounts (the two carried-over majors), blank or empty identifiers and codes, simultaneous operations on one cart: reserved.
- Several promotions, stacking, promotion variants (fixed amount, free delivery), expiry, usage limits, per-dish promotions, tax, tip, extra fee lines, UI, payment, order handoff, configuration adapter, ports.
- Any `Double`, `Float`, `BigDecimal`; any default amount, rate, threshold, currency or code.
- A defensive `min(discount, subtotal)` clamp.

## 8. Deviations

(empty)

## 9. Self-review

(empty)

## 10. Follow-up actions

(empty)
