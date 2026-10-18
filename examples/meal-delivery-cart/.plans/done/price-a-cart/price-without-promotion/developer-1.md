---
role: developer
status: done
reasons: []
---

# Developer note, iteration 1: price a cart, story 1 (price-without-promotion)

Skills announced and applied: `plan-driven-dev` (implementation and closing steps) and `behavior-driven-testing`. The plan was followed step by step, with no deviation and no question to the product owner. Stack note: `kotlin.test.Test` is not available offline, so tests use JUnit's `@Test` with `kotlin.test` assertions.

## Commits (on the shared branch, nothing pushed; only files under this folder)
1. `7d50980` subtotal is the exact sum (types, pricing function, entry point) + test-case `subtotal-is-the-exact-sum`
2. `c1ffa13` zero discount, fee line, total, result shape + test-cases `no-discount-without-promotion`, `result-exposes-every-line`, `fee-line-is-the-rules-fee`, `total-adds-up`
3. `fb41f5a` empty cart: zeros and no fee line + `empty-cart-has-no-fee-line`
4. `17e1b75` quantity zero refused + `quantity-zero-refused`
5. `54ff945` currency of the rules, line in another currency refused, fee in another currency refused + 3 test-cases
6. `a0a7948` only the changed rule moves the result + `only-the-changed-rule-moves`
7. `27a2447` same input same result / order / cart unchanged and list copied + 2 test-cases
8. `e353b6c` same line twice, free lines keep the fee + 2 test-cases
9. `a43f5c4` reads `minorUnits` through the public accessor (mutation survivor, see below)

15 tests in `PriceCartTest`, 15 test-cases under `docs/business/test-cases/price-a-cart/`, each with `source` and the exact `automated_test`. Each test was seen red before its code, except where the behavior was already produced by earlier code (B6 amounts in the rules' currency, the line-in-another-currency refusal, B7, B8 and E1/E6 were green at once; B7 and B8 were checked by temporarily breaking the production code, which turned them red; the break was reverted, not committed).

## Gauntlet (final)
- `tools/harness/_maven.sh -o test` (resolved Maven, offline): 15 tests, 0 failures.
- `bash tools/harness/run_all.sh --with-mutation`: exit 0. INV-001..004 exit 0; INV-005: 15 covered_ok, 0 broken, 0 pending, 0 orphan; mutation critical ran.
- Step 10 (D-30): no guard and no test for negative or overflowing amounts; checked that no test-case or test states such a behavior.

## Mutation (scope critical, default mutators, no threshold written)
- First run: 83.3% (10 killed / 12 generated). Survivors: `Money.getMinorUnits` return replaced by 0 (whole-value comparisons never read the accessor) and `requireSameCurrency` call removed in `Money.minus`.
- The first one was a real gap: a caller reads the amount through `minorUnits`. Fixed with a behavior assertion (`assertEquals(1900L, price.subtotal.minorUnits)`), not a mutant-killing test.
- Final run: **91.7% (11 killed / 12 generated)**. One survivor: `Money.kt:14`, `Money.minus` no longer checks that both amounts are in one currency. It cannot be reached through `PriceCart` (subtotal, discount and fee line are always in the rules' currency by construction), so no behavior at the plan's test boundary protects it. Options for the human/reviewer: a direct `Money` test (a new test class, in the sensitive zone `domain.money`, outside the plan: not done), or removing the unused `minus` guard. Left as is.
- PIT noise on Kotlin bytecode, as observed on this code: no mutant on the compiler's generated null checks, none on data-class `copy`/`componentN`/`equals`/`hashCode`/`toString`, none unviable, none from the inline `fold` (stdlib inline, outside the target). Getter mutants appear only for primitive and nullable returns (`getMinorUnits`, `getQuantity`, `getLines`, `getFeeLine`); non-null object getters (`getSubtotal`, `getCurrency`...) are not mutated by the default set. The default mutators do not touch the `Math.*Exact` arithmetic, so a wrong operator in `plus`/`minus`/`times` would not produce a mutant: the 12-mutant sample says little about arithmetic, which only the tests protect. Observed noise: none; observed blind spot: arithmetic.

## Behaviors added (public, not literally stated by the plan or the decisions)
- Entry point shape: `PriceCart.price(cart: Cart, rules: PricingRules): Price` (an `object`); the plan said only "thin entry point".
- `Price(subtotal, discount, feeLine: Money?, total)`: `feeLine` is a nullable `Money` (null = absent for the empty cart, D-31). Story 2 adds a trailing property.
- `Cart(lines: List<CartLine>)` exposes `lines` (a defensive copy, read-only type); `Cart` is not a data class, so two carts are not `equals`.
- `CartLine(unitPrice: Money, quantity: Int)` refuses exactly `quantity == 0`; a negative quantity is accepted (reserved by D-30, undocumented natural behavior).
- `PricingRules(currency, deliveryFee: Money)` is a data class with no default.
- `Money` public API: `plus`, `minus`, `times(Int)`, `zero(currency)`; they raise `IllegalArgumentException` on mixed currencies and `ArithmeticException` on overflow (the `Math.*Exact` choice of the plan; the overflow behavior is reserved, D-30, and untested).
- A line in another currency than the rules gives `IllegalArgumentException` from `PriceCart.price` (plan B6); the same exception for a zero quantity and a fee in another currency (plan).
None of these needs a new decision beyond the plan and the logged ones; the two a consumer will meet first (nullable `feeLine`, `ArithmeticException` on overflow) are covered by D-31 and D-30.

## For the reviewer
- Sensitive zone created: `domain.money` and `domain.pricing` (a person reviews the diff). Story 1 rounds nothing; no rounding function, no `Percentage`.
- Plan section 9/10 and the plan file were not touched (instructions).
