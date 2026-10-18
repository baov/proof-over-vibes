---
role: planner
status: done
reasons: []
---

# Price a cart, story 1: price without promotion

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress (D-30 to D-32 answered: D-30, D-31, D-32)

## 2. Goal

The caller gives cart lines (unit price, quantity) and the money rules (currency, flat delivery fee) and receives the breakdown (subtotal, discount, fee line, total), exact, in the rules' currency, deterministic, the cart untouched. No promotion exists yet: the discount is always zero. This story lays the types Story 2 extends. Acceptance criteria: Story 1 of `../stories.md` (1..14), nothing else.

## 3. Context

Sources read: brief (story and parent), `stories.md`, `architect.md` (front-matter and ADRs final), ADR-0001/0002, `invariants.md`, decision log D-1..D-29, PRD, the harness (`check_layers.py` rules via `ArchitectureTest`, `check_test_coverage.py`, `run_all.sh`). No `FEEDBACK.md` exists. No feature code exists: `src/main` and the business test-cases do not exist yet.

**Layout** (base package `io.example.mealcart`, stack fixed: Kotlin 2.2.0, JDK 21, Maven offline through `tools/harness/_maven.sh`, `kotlin-test` + JUnit Jupiter 5.12.2):
- `domain/money/Money.kt`: `Money(minorUnits: Long, currency: java.util.Currency)`.
- `domain/cart/CartLine.kt`, `domain/cart/Cart.kt`.
- `domain/rules/PricingRules.kt`.
- `domain/result/Price.kt`.
- `domain/pricing/Pricing.kt`: the pure pricing function.
- `application/PriceCart.kt`: the entry point the caller uses.
- Tests: one class, `src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt` (boundary: the entry point; construction refusals are reached through the types the caller builds).

**Invariants that apply** (from `docs/technical/invariants.md`; run `bash tools/harness/run_all.sh` after each green):
- INV-001 `domain` imports only the Kotlin/JDK stdlib; `application` imports `domain` only.
- INV-002 only `domain.money` rounds. Story 1 rounds nothing (subtotal exact R14, fee unchanged D-26): no rounding function is written now; Story 2 introduces it in `domain.money`.
- INV-003 no `Double`, `Float`, `BigDecimal`. No `Percentage` in Story 1 (the rate is Story 2).
- INV-004 purity: no clock, randomness, I/O, `System`, `java.util.concurrent`.
- INV-005 each test-case points at an existing test, each test class has a test-case (`ArchitectureTest` excepted). Test-cases below are created with their test, never before (a reference to a missing test is an error, exit 1).
- INV-006 mutation on `domain` and `application`, no threshold: run `run_mutation.sh --scope diff` at closing.
- Sensitive zone (money): `domain.money` and `domain.pricing` and their tests need a human decision. This plan creates both; the escalation is the Reviewer's, and a person reviews the diff of these zones.

**Decisions this plan applies** (not reopened): hexagonal light; `Money` in minor units `Long` with the currency; `CartLine` refuses quantity zero at construction (`require`, `IllegalArgumentException`) so a `Cart` never holds one; `PricingRules` is an immutable value built by its constructor, no default for any amount or currency, and rejects a delivery fee whose currency is not its own (`IllegalArgumentException`); a line holds unit price and quantity only; pricing is a stateless function returning a new `Price`; D-24 (empty cart: zeros and no fee line); D-26 (fee in minor units, unchanged).

**Technical choices** (nothing a caller can observe; for the reviewer to challenge):
- `Cart` copies the list it is given (`lines.toList()`), so a caller mutating its own list later cannot change a cart already built.
- `Money` arithmetic helpers (`plus`, `minus`, `times(quantity)`) live in `domain.money`, use `Math.*Exact`, and `require` the same currency.
- The pricing function is top-level in `domain.pricing`; `application.PriceCart` is a thin entry point calling it (named by the ADR: "one pricing entry point"), no state.
- `Price` is a `data class`: equality by value, so "same input, same result" is testable with `assertEquals`. Its constructor is only called by pricing.
- Test fixtures: a private helper in `PriceCartTest` builds rules and lines; two currencies in the tests (EUR with 2 fraction digits, JPY with 0) so nothing depends on a built-in currency and "smallest unit" is not assumed to be hundredths.
- Exception tests assert the type (`IllegalArgumentException`), not the message text.
- No `Money.ZERO` constant (currency-less zero is impossible): a `Money.zero(currency)` factory.

**Conflicts between documents**: the architect note says the fee goes through the rounding function; D-26 (the fee parameter is already in minor units, AC12) supersedes it. Story 1 rounds nothing and the fee line equals the parameter unchanged. The architect note is not edited.

**Extension for Story 2 (planned, not decided here)**: Story 2 adds, never changes: (a) one trailing property to `Price` for the reason a promotion did not apply (the architect suggests a nullable closed type; Story 2 settles); (b) one trailing optional parameter (the code) to `PriceCart` and the pricing function; (c) the promotion part (code(s), rate, minimum) to `PricingRules`, whose default/optionality Story 2 decides; Story 1 tests build rules with currency and fee only. Story 1 therefore has no code parameter, no reason property, no `Percentage`, no rounding function.

## 4. Expected behaviors

Test boundary of every behavior: `PriceCart` (application entry point) called with a `Cart` and `PricingRules`; the refusals are observed at the construction call that raises them (`CartLine(...)`, `PricingRules(...)`) or at the `PriceCart` call. All in `PriceCartTest`. Amounts in minor units. Result shape: named fields (D-31, AC13).

Nominal and acceptance criteria (AC = Story 1 criterion):
- **B1 subtotal (AC1)**: given lines (350 x 2) and (1200 x 1) in EUR, when priced, then subtotal 1900.
- **B2 four named fields in order (AC2, AC13)**: given any cart, when priced, then the result exposes subtotal, discount, feeLine, total, in that order (R2).
- **B3 no discount (AC3)**: given any cart, when priced, then discount is `Money(0, rules currency)`.
- **B4 fee line (AC4, AC12)**: given a delivery fee of 250 in the rules, when priced, then the fee line equals `Money(250, currency)` unchanged, whatever the subtotal.
- **B5 total (AC5)**: given subtotal 1900 and fee 250, then total 2150, and total equals subtotal - discount + feeLine.
- **B6 currency (AC6, AC11)**: given rules in JPY, then every amount of the result, including the zero discount, is in JPY; given rules in EUR, then in EUR. A line whose unit price is in another currency than the rules makes pricing fail with `IllegalArgumentException`, no result.
- **B7 only the changed rule moves (AC7)**: given the same cart, when only the delivery fee changes, then subtotal and discount are unchanged, the fee line and the total move by that difference; when only the currency changes, then only the currency of the amounts changes.
- **B8 determinism and immutability (AC8)**: given the same cart and rules, when priced twice, then the two results are equal; the cart's lines are unchanged afterwards; a caller mutating the list it passed to `Cart` after building it does not change the price.
- **B9 empty cart (AC9)**: given a cart with no lines, then subtotal, discount and total are zero in the rules' currency and the fee line is absent (D-24), even when the fee parameter is positive.
- **B10 quantity zero (AC10)**: given a line of quantity zero, when it is built, then `IllegalArgumentException` is raised; no `Cart` holding it exists, so no price is returned.

Edge cases the plan adds (the 'twice / nothing / invalid / edge / order' pass):
- **E1 same line twice**: given two equal lines (350 x 2) in one cart, then both count (subtotal 1400); lines have no identity (D-27) and nothing merges them (R1: sum over lines).
- **E2 order**: given the same lines in a different order, then the result is equal.
- **E3 quantity one, and a one-line cart**: subtotal equals the unit price.
- **E4 zero fee [derived from AC4/AC12]**: given a delivery fee of 0 and a non-empty cart, then the fee line is present and zero (the fee line equals the parameter unchanged), total = subtotal.
- **E5 fee in another currency than the rules**: given a `PricingRules` built with a fee whose currency differs from the rules' currency, then `IllegalArgumentException` at construction (architect).
- **E6 unit price zero [D-32, AC14]**: given a non-empty cart whose lines all have unit price 0, then subtotal 0, discount 0, and the fee line is present and equals the fee, total = fee.
- **E7 negative or overflowing amounts [D-30]**: reserved: no rule, no test, no test-case; the code is not given a guard for them.

**Business test-cases** (`docs/business/test-cases/price-a-cart/<slug>.md`, one per behavior, created WITH the test that covers it). Front-matter exactly:

```
---
feature: price-a-cart
type: functional
priority: high            # medium for E1..E3
source: PRD R1, R14; Story 1 criterion 1     # the references of the line
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::<test name>
status: covered
---

# <title>

- Given: ...
- When: ...
- Then: ...
```

| Slug | Behavior | Test name (backticked in Kotlin, written verbatim in `automated_test`) | source |
|---|---|---|---|
| subtotal-is-the-exact-sum | B1, E3 | `the subtotal is the sum of unit price times quantity` | PRD R1, R14; Story 1 c.1 |
| result-exposes-every-line | B2 | `the result exposes subtotal, discount, fee line and total` | R2, D-31; c.2, c.13 |
| no-discount-without-promotion | B3 | `the discount is zero` | R11; c.3 |
| fee-line-is-the-rules-fee | B4, E4 | `the fee line is the delivery fee of the rules, unchanged` | R12, D-10, D-26; c.4, c.12 |
| total-adds-up | B5 | `the total is subtotal minus discount plus the fee line` | R13, R16; c.5 |
| amounts-in-the-rules-currency | B6 | `every amount is in the currency of the rules` | R15, D-13; c.6 |
| line-in-another-currency-refused | B6 | `a line priced in another currency than the rules is refused` | R15, D-27; c.11 |
| only-the-changed-rule-moves | B7 | `changing one rule parameter changes the result and nothing else` | R4, R6, D-2; c.7 |
| same-input-same-result | B8, E2 | `the same cart and rules give the same result, whatever the line order` | R3, R5; c.8 |
| cart-unchanged-by-pricing | B8 | `pricing leaves the cart unchanged` | R5; c.8 |
| empty-cart-has-no-fee-line | B9 | `an empty cart gives zero amounts and no fee line` | R17, D-24; c.9 |
| quantity-zero-refused | B10 | `a line of quantity zero is refused` | R18, D-24; c.10 |
| same-line-twice-counts-twice | E1 | `the same line twice in a cart counts twice` | R1; c.1 (derived) |
| fee-in-another-currency-refused | E5 | `rules with a fee in another currency are refused` | R15; architect.md (rules validation) |
| zero-price-cart-still-has-fee | E6 [D-32, AC14] | `a cart of free lines still has the fee line` | R12, R17, D-32; c.14 |

(E4 is asserted inside the fee-line test with a second case; E3 inside the subtotal test.) Each test name above must appear in `PriceCartTest.kt` exactly as written.

## 5. Steps

Order is TDD, one behavior at a time (red, green, refactor), `bash tools/harness/run_all.sh` after each green, and each test-case file created with its test. Maven: `tools/harness/_maven.sh -o test`.

- [ ] Step 1: Create `src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt` with the B1 test (red). Create `domain/money/Money.kt` (data class `Money(minorUnits, currency)`, `zero(currency)`, `plus`, `times(quantity)`, same-currency `require`), `domain/cart/CartLine.kt` (unit price, quantity, refuses quantity 0), `domain/cart/Cart.kt` (copies its list), `domain/rules/PricingRules.kt` (currency, delivery fee), `domain/result/Price.kt`, `domain/pricing/Pricing.kt`, `application/PriceCart.kt`, only as much as B1 needs. Green. Create the `subtotal-is-the-exact-sum` test-case. [quantity type Int; arithmetic uses Math.*Exact, overflow behavior reserved, D-30]
- [ ] Step 2: B2 + B3 (`Price` exposes `subtotal`, `discount`, `feeLine`, `total` in that order; discount `Money.zero(currency)`). [named fields, D-31] Test-cases `result-exposes-every-line`, `no-discount-without-promotion`.
- [ ] Step 3: B4 + B5 + E4: fee line from `PricingRules.deliveryFee`, total = subtotal - discount + fee line; `Money.minus`. Test-cases `fee-line-is-the-rules-fee`, `total-adds-up`.
- [ ] Step 4: B9: empty cart, `feeLine` absent and zeros in the rules' currency. Test-case `empty-cart-has-no-fee-line`.
- [ ] Step 5: B10: `CartLine` quantity-zero refusal tested through the constructor (`assertFailsWith<IllegalArgumentException>`), and `Cart` cannot hold it. Test-case `quantity-zero-refused`. The guard is NOT written in step 1: the test is red first, then the guard.
- [ ] Step 6: B6 + E5: result currency follows the rules (EUR and JPY); `PricingRules` rejects a fee in another currency; pricing refuses a line in another currency (`IllegalArgumentException`). Test-cases `amounts-in-the-rules-currency`, `line-in-another-currency-refused`, `fee-in-another-currency-refused`.
- [ ] Step 7: B7: parameterized-by-fee and by-currency comparisons (no new production code expected; if the test is green at once, check by changing the production code temporarily that it can fail). Test-case `only-the-changed-rule-moves`.
- [ ] Step 8: B8 + E2: equality of two results, order-independence, cart unchanged, copy of the caller's list. Test-cases `same-input-same-result`, `cart-unchanged-by-pricing`.
- [ ] Step 9: E1 same line twice; E6 free lines [D-32, AC14]. Test-cases `same-line-twice-counts-twice`, `zero-price-cart-still-has-fee`.
- [ ] Step 10: nothing for negative or overflowing amounts (D-30, reserved): no test, no guard, no test-case; check no such behavior was documented by accident.
- [ ] Step 11: closing: `tools/harness/_maven.sh -o test`, `bash tools/harness/run_all.sh` (INV-001..005), `bash tools/harness/run_mutation.sh --scope diff` (INV-006, no threshold: record the score in section 9), then run the plan through the "wrong direction signals" of `behavior-driven-testing`.

Test-case checks: `python3 tools/harness/check_test_coverage.py` must report 0 pending, 0 broken, 0 orphan at the end.

## 6. Risks & edge cases

- Sensitive zone: `domain.money` and `domain.pricing` are created here; a wrong sum is a wrong price shown. The Reviewer escalates changes to these zones and a person reviews their diff (this plan is not that decision); Story 2 changes to them go through the same path.
- Mutation noise on Kotlin data classes (getters never read, `copy`/`componentN`): tests read all four fields of `Price` and compare whole values, so equality is exercised. Exclusions in `pom.xml` only with a comment.
- `Money` `data class` equality: `Currency` instances are singletons, so equal currency means `==`; two `Money` are equal only with the same minor units AND currency (0 EUR is not 0 JPY). Tested through B6.
- Story 2 compatibility: Story 1 tests build rules with currency and fee only; Story 2 must add its promotion part without breaking them, or update them knowingly (a deviation then).
- Not tested here, left reserved (PRD section 6): negative or overflowing amounts [D-30], blank or empty identifiers and codes (no identifier exists in Story 1: lines have none, no code yet), two operations on one cart at the same moment (pricing is a pure function over immutable inputs; the business meaning stays reserved, no test).
- An `Int` quantity with a `Long` price: the `times` overflow path exists in code as soon as `Math.multiplyExact` is used; reserved, D-30.

**Questions answered** (`answers.md`, all `answered-by-delegate`): D-30 negative or overflowing amounts stay reserved (D-30); D-31 named fields in R2 order, fee line absent for the empty cart (D-31); D-32 zero subtotal accepted, fee line applies (D-32). Nothing consumer-visible remains open.

## 7. Out of scope

- Promotion code, rate, minimum, reasons for non-application, `Percentage`, the rounding function: Story 2.
- Negative or overflowing amounts, blank or empty identifiers and codes, simultaneous operations on one cart: reserved, only as D-30 decides.
- Tax, tip, extra fee lines, UI, payment, order handoff, catalogue, configuration adapter, port of any kind.
- Any `Double`, `Float`, `BigDecimal`; any default amount, rate, threshold or currency.

## 8. Deviations

(empty)

## 9. Self-review

(empty)

## 10. Follow-up actions

(empty)
