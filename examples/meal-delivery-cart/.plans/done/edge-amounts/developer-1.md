---
role: developer
status: done
reasons: []
---

# Developer, iteration 1: edge cases on amounts (A1..A12)

Skills announced and applied: `plan-driven-dev` (step 5 and 6) and `behavior-driven-testing`. The plan was followed with no deviation; all steps done. Red first was observed at each step (the exception being the cases that already held, below).

## Commits (on the shared branch, only files under this folder)

1. `f227bc4` Refuse negative quantity, unit price, fee and promotion minimum (B1..B5)
2. `5715d25` Refuse an amount beyond the money range with AmountTooLargeException (M1..M3, B6a, B6b, B7, B9)
3. `4d5d63b` Take a rate with a wide product so every scale prices exactly (B15..B18, M4, M5)
4. `ace950d` Pin the total, idempotence, line order, empty cart and code on huge amounts (B8, B10..B13; characterization, see below)
5. `a0ff7b4` Refuse a foreign currency before any amount and a rate of a negative operand (B14 = D-42, M6 = D-44)

Code touched: `domain.money` (`Money`, new `AmountTooLargeException`), `domain.cart.CartLine`, `domain.rules.PricingRules`, `domain.pricing.Pricing.kt` (a currency pre-pass only; no catch, no clamp, order `subtotal - discount + fee` kept). Tests: `EdgeAmountsTest` (new, 19 tests) and `MoneyTest` (+6). 25 new business test-cases (`price-a-cart/`), all `status: covered`. Existing tests unchanged (no existing test was edited; the plan said 54 existing tests, the repo had 37 `@Test` before this work: PriceCartTest 15, ApplyPromotionTest 19, MoneyTest 3; the count in the plan seems to include something else, I changed none of them).

## Gauntlet (final)

- `tools/harness/_maven.sh -o test`: 62 tests, 0 failure.
- `bash tools/harness/run_all.sh --with-mutation`: exit 0. INV-001..004 pass (`BigInteger` accepted, no amendment); INV-005: 60 test-cases, 60 covered_ok, 0 pending, 0 broken, 0 orphan.
- Mutation (scope critical, PIT): **81.3 % (61 killed / 75 generated)**; no threshold set (human decision, none written).
- Survivors (14), my reading of each, for the reviewer to challenge:
  - 9 x `Money.kt:35-37` `VoidMethodCallMutator`, removed `Intrinsics.checkNotNull` / `checkNotNullExpressionValue`: Kotlin null-check intrinsics generated for the `BigInteger` platform types in `times(Percentage)`; nothing observable, equivalent.
  - 1 x `Money.kt:46` `PrimitiveReturnsMutator` on `exactly`: `exactly` is `private inline`; the call sites carry their own inlined copy, the out-of-line body is dead code, equivalent.
  - 2 x `Pricing.kt:27` `RemoveConditionalMutator_EQUAL_ELSE`: bytecode offset 23..39 of the inlined `all { }` (my currency pre-pass): the `is Collection && isEmpty()` shortcut of the stdlib `all`; skipping it gives the same result (an empty loop returns true), equivalent. The real currency check is killed (B14, `PriceCartTest` foreign line).
  - 1 x `Percentage.getScale` (known, carried over, untouched).
  - No survivor on `CartLine`, `PricingRules`, or on the rounding/range comparisons of `Money`.

## Step 6, manual mutation of the exact calls (reverted by file copy each time; tree clean afterwards, never in a commit)

| Replacement | Result | Behaviors that failed |
|---|---|---|
| `Math.addExact` -> `+` | killed | M1 (`adding stops exactly...`), B6b, B7, B8, B10, B11, B13, B9 (8 tests) |
| `Math.subtractExact` -> `-` | killed | M2 only (`subtracting stops exactly...`): no pricing path reaches a subtraction overflow, since discount <= subtotal; the plan expected M2 |
| `Math.multiplyExact` -> `*` | killed | M3 and B6a |
| `longValueExact()` -> `toLong()` | killed | M4 and M5 (not B-level: pricing cannot reach a share beyond the range, as the plan states) |
| conversion -> rethrow of the raw exception | killed | 13 tests (every test asserting `AmountTooLargeException`: M1..M5, B6a..B8, B9, B10, B13) |
| total as `subtotal + fee - discount` | killed | B8 (`a total that fits after the discount is accepted...`) |

## Notes on the red/green cycle

- B5, B10..B13, B16 and B18 passed on first run: they characterize behavior that already held (or that the earlier steps made hold). B16 was expected red at scales 15..18 by the plan, but with subtotals of at most 10^17 the old product `x5` does not overflow; the half-up rule itself was already right. B15 and B17 (largest subtotal), M4 and M5 were red. Not weakened, kept as regression guards.
- B14 and M6 were red before step 5.

## Behaviors added

- Everything below is in the plan or a decision; nothing else is public:
  - `AmountTooLargeException(message: String) : ArithmeticException` in `domain.money` (ADR-0003, D-38, D-43). The message names the operation and the two operands for a human; no test pins it.
  - `CartLine`, `PricingRules`: new `IllegalArgumentException` refusals for negative quantity, unit price, fee, promotion minimum (D-37).
  - `price` refuses a line whose currency differs from the rules before computing any amount (D-42).
  - `Money.times(Percentage)` refuses a negative amount or numerator (D-44); `Money.plus/minus/times(Int)` throw the new type instead of the raw `ArithmeticException`.
- Not a decision, an implementation consequence, listed for transparency: `Money(Long.MIN_VALUE, c)` stays buildable and `Money.times(Int)` accepts negative quantities (signed arithmetic, plan section 3). No consumer-visible behavior without a document: no question.

## Open points for the reviewer

- The sensitive money zone is touched (`domain.money`, `domain.pricing`): a person should read the diff. Risk spots: `Money.times(Percentage)` (wide product, half up once, narrowing) and the order in `price`.
- The merge with `edge-codes-and-concurrency` (not started, not touched) will meet this change on `PricingRules.init` and `Pricing.kt`; both small.
- Self-review against the "wrong direction signals": tests are at the boundary (`PriceCart`, `Money` API for what pricing cannot reach), named after behaviors, assert types never messages, no mocks. `EdgeAmountsTest` pins literal boundary values (max, max - 5, ...) on purpose: they are the specification of the range.
- Follow-up (not done, out of scope): `Percentage(10,2) != Percentage(100,3)`; mutation threshold; the plan's "54 existing tests" figure to correct.
