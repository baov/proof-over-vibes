---
role: developer
status: done
reasons: []
---

# Developer note, iteration 1: story 2 (apply a promotion)

Skills announced and applied: `plan-driven-dev` (implementation steps) and `behavior-driven-testing`. Plan followed step by step; no deviation. Story 1 tests unchanged and green.

## Commits (9, branch `claude/bank-account-poc-1435f8`, nothing pushed)

1. `7c92641` a valid code takes the rate off the subtotal (Percentage, Promotion, PromotionNotApplied, trailing parameters)
2. `22e4460` the discount is rounded once, half up
3. `e5bbccf` the total adds up with a discount; `Money.minus` tested on the Money API
4. `161ddc6` an unknown code gives no discount and says why
5. `168e18b` below the minimum gives no discount; the minimum itself applies; unknown code wins
6. `4419330` empty cart, no code, discount that rounds to zero (existing `no-discount-without-promotion` edited)
7. `098a24e` rate bounds, scale bounds and minimum currency refused by construction
8. `4b5d2d2` cap and untouched fee
9. `aba2313` quantity zero, exact code match, same input twice

## Tests and test-cases

- `ApplyPromotionTest` (boundary `PriceCart`, plus the construction of `PricingRules` and `Percentage`): 19 tests. `MoneyTest` (boundary `Money`): 3 tests. `PriceCartTest` untouched: 15 tests. 37 in all, green.
- 20 test-case files created (the 20 rows of the plan table), 1 edited; `check_test_coverage.py`: 35 test-cases, 35 covered_ok, 0 pending, 0 broken, 0 orphan.
- Red/green: every behavior was written first. Steps 1, 2, 4 (unknown code, below minimum) and 6 were genuinely red. Behaviors the earlier code already satisfied (E7 sums, B3 equality, B6, B7, B9, B10, B11, E1, E3, E4, E8) were green on first run; the plan's mutation checks stand in for red there.

## Temporary mutation checks (all reverted, none committed)

- `2 * remainder >= divisor` to `>` : killed (exact-half test, 1010 at 5 percent).
- `subtractExact` to `addExact` in `Money.minus`: killed.
- `Money.minus` ignoring its operand: killed.
- `total = subtotal + discount + fee`: killed.
- Removing the same-currency guard in `minus`: killed (`MoneyTest`).
- Incident, no effect on the result: while reverting a mutation with `git checkout` I also dropped an uncommitted half-up edit in `Money.kt`; it was re-applied before commit 2 and the suite re-run green. Later checks used file copies.

## Gauntlet

- `tools/harness/_maven.sh -o` test: 37 tests green. `run_all.sh`: INV-001..004 exit 0, INV-005 exit 0.
- `run_all.sh --with-mutation` (scope critical): **score 98.0% (48 killed / 49 generated)**, no threshold written (human decision).
- Surviving mutant (1): `Percentage.kt:7` PrimitiveReturnsMutator, `Percentage::getScale` returns 0. `scale` is read in production only by the text of the out-of-range-rate message in `PricingRules`, which the plan says is not a contract and has no test. No behavior to protect, so no mutant-killing test was written; for the human to exclude or accept. All rounding mutants (`>=`, remainder, quotient) and the `minus`/total mutants are killed. `Math.*Exact` is not mutated by the default PIT mutators; the behavior tests above protect it.

## Behaviors added (not stated in the plan, or only implied)

- `Money` gains a public `operator fun compareTo(other: Money)` that refuses mixed currencies (`IllegalArgumentException`), as `plus`/`minus` do. The plan names `Money.compareTo` with the same-currency guard; a `MoneyTest` test states the comparison and the refusal. It has no business test-case file of its own (INV-005 requires none). Consumer-visible only to Kotlin callers using `<` on `Money`; consistent with ADR-0002.
- `Percentage.denominator` is `internal` (10 to the scale), used by `Money.times` and the rules; not part of the public API.
- `Percentage`, `Promotion` are data classes (equality, `copy`, `toString`); `PricingRules` equality now includes the promotion. No decision needed.
- The scale refusal message and the out-of-range-rate message are not pinned by a test (as planned).
- Nothing else. No consumer-visible behavior lacks a document.

## Reserved, left alone

Negative amounts and overflow (no guard, no test): `Math.multiplyExact(minorUnits, numerator)` raises a raw `ArithmeticException` on overflow, like the other sums; a negative subtotal's rounding is not defined. Blank or empty codes and two operations on one cart: not guarded, not tested. Percentage with a negative numerator can be built (D-36) and is refused by the rules.

## For the reviewer (sensitive zone: money)

- Rounding lives in `Money.divideHalfUp` (`domain.money`, INV-002); `domain.pricing` never divides. No `min(discount, subtotal)` clamp (plan).
- Decision order in `Pricing.kt`: no code, unknown code (or no promotion), below minimum, apply. The minimum is compared with the exact subtotal.
- Plan step 1 listed the scale guard in `Percentage`; it was added in step 6 with its test (red first). Same end state, no deviation.
