---
role: reviewer
status: escalate
verdict: GO
reasons:
  - gauntlet green (62 tests, INV-001..005, mutation critical 81.3 percent, all 14 non-killed mutants read and none hides a defect); no blocking finding, no major finding, 4 minor
  - escalate: the diff touches the sensitive zone "Money computation and rounding" (domain.money, domain.pricing); a person must read this diff before merge
severity: minor
open_majors: []
---

# Pre-merge review: price a cart, edge cases on amounts (A1..A12), n=1

**Verdict: GO** (status `escalate`, sensitive zone)
**Date**: 2026-10-18. **Base**: bbdca93..a0ff7b4. **Scope**: `examples/meal-delivery-cart` only, 32 files, +742 / -15 (6 production files, about 55 lines; 2 test classes, 346 lines; 25 new test-case files).
**Criticality**: critical. Signals: domain layer; money computation and rounding (declared sensitive zone); public signatures consumed by callers (`Money`, `CartLine`, `PricingRules`, new public `AmountTooLargeException`).

## Summary

The change does what A1..A12 ask and nothing else. I rebuilt the arithmetic against an independent `BigInteger` reference outside the repository, over about 12.5 million cases (rate share at every scale 0..18, exact halves, `Long.MAX_VALUE`, 100 percent, plus/minus/times, and whole prices with the total order `subtotal - discount + fee`): no mismatch, no silent wrap, no spurious refusal, no missed refusal. The Developer's reading of the survivors holds (with one miscount, m2), and I reproduced every manual mutation of the exact calls. What is left is minor: an eagerly built exception message, a note that miscounts, a plan file not brought up to date, and a mutation baseline for a person to set. No consumer-visible behavior is left unsettled: every one maps to A1..A12, ADR-0003 or D-37..D-44. The zone is sensitive, so a person reads the diff before merge.

## Gauntlet

| Check | Result |
|-------|--------|
| Test suite | OK: 62 tests, 0 failures (`EdgeAmountsTest` 19, `PriceCartTest` 15, `ApplyPromotionTest` 19, `MoneyTest` 9); run in the project and in a scratch copy |
| Lint / format | not available (no linter in `pom.xml` or the pre-commit config; same as the earlier stories) |
| Harness invariants | OK: INV-001..004 exit 0 (`BigInteger` accepted, no amendment needed) |
| Test-case bridge | OK: 60 test-cases, 60 covered_ok, 0 broken, 0 pending, 0 orphan |
| Mutation (diff, critical) | `bash tools/harness/run_all.sh --with-mutation` exit 0. 81.3 percent (61 killed / 75), no threshold set. 13 SURVIVED + 1 NO_COVERAGE, all read below (none real) |
| Test-cases touched | 25 read (all new, `price-a-cart/`); the 35 older ones skimmed by name, none modified (`git diff` shows 0 deleted lines under `src/test`) |

Four-angle review performed: the gauntlet is green.

## Independent verification (scratch copy outside the repository)

- **Wide product, half up, narrowing.** Java driver on the compiled classes against a `BigInteger` oracle: 2,000,000 random and boundary `Money.times(Percentage)` (all scales 0..18, numerators from 0 to `Long.MAX_VALUE` so results both inside and beyond the range, amounts `0..Long.MAX_VALUE` with a bias to the edges), plus constructed exact-half cases at every scale (the product is a half unit below and above a boundary: always rounds up), plus 100 percent and 0 percent of `Long.MAX_VALUE` at all 19 scales. 0 mismatch; `AmountTooLargeException` exactly when the rounded share exceeds `Long.MAX_VALUE`, never otherwise.
- **No silent wrap.** 3,000,000 random `plus`, `minus`, `times(Int)` including `Long.MIN_VALUE`, `Int.MIN_VALUE`, `Int.MAX_VALUE`: 0 mismatch (wrong value, wrap, or wrong exception type).
- **Total order.** 1,500,000 random whole pricings (0..4 lines, quantities up to `Int.MAX_VALUE`, fees near `Long.MAX_VALUE`, promotions at every scale, known/unknown/no code, minimum 0 or large): reference subtotal (each line and each partial sum checked), discount, total `subtotal - discount + fee` in `BigInteger`. Priced 646,349, refused 853,651, 0 mismatch; no price carries a negative amount. A refusal happens exactly when the subtotal does not fit, or the final total does not fit; `subtotal + fee - discount` would have been wrong and the plan's B8 test catches it (below).
- **A4, every named amount can be refused.** Subtotal: line (B6a) and sum (B6b), proved through `price`. Total: B7/B8, proved through `price`. Discount: not reachable through `price` (rate at most 100 percent), proved at `Money` level (M4: `max x Percentage(2,0)`, `Percentage(Long.MAX_VALUE,18)`). Fee line: it is a `Money` held by the rules, so it cannot be unrepresentable by itself; it makes the *total* refuse (B7). This reading is consistent with the plan (section 3) and ADR-0003; no behavior is missing.
- **A5, a refused call changes nothing.** `Cart` copies its list, `Money`, `CartLine`, `PricingRules` are immutable data classes; pricing a refused cart twice refuses twice with `lines` unchanged; `copy()` of a `CartLine` with a negative price or quantity goes through `init` and is refused.
- **Orders against D-42/D-44.** Probed: oversized line then foreign-currency line, and foreign then oversized: `IllegalArgumentException` in both (D-42). Negative fee together with a foreign fee currency, rate above 100 percent together with a negative minimum, scale 19 or -1, negative quantity together with negative price: all `IllegalArgumentException` at construction (type only observable, as the plan states). `Money(-1) x rate` and `Money x Percentage(-1)` raise `IllegalArgumentException`; `Money(Long.MIN_VALUE) x Percentage(0)` also (amount checked before the numerator, D-44: zero accepted, a negative amount is not). Negative never reaches pricing, so negative-versus-too-large cannot be observed through `price`.

## Survivors: the Developer's reading, challenged

- **Null-check intrinsics, `Money.kt:35-37`.** Counted from `mutations.xml`: **10**, not 9 (3 at :35, 1 at :36, 6 at :37), all `VoidMethodCallMutator` on `checkNotNull` / `checkNotNullExpressionValue` for the platform-typed results of `BigInteger.multiply`, `divideAndRemainder` (components), `BigInteger.ONE`, `plus`, `valueOf`. None of those can return null, so removing the check changes nothing observable: equivalent. Reading holds; the number is wrong (m2).
- **`Money.kt:46`, `exactly`.** PIT's status for it is `NO_COVERAGE`, not SURVIVED, and `javap -p -c` shows `private final long exactly(String, Function0)` is declared but never invoked (all call sites are inlined copies). Dead out-of-line body of a `private inline` function: equivalent. Holds.
- **`Pricing.kt:27` pair.** Line 27 is the stdlib line mapped from the inlined `all { }` (`is Collection && isEmpty()` shortcut), at bytecode offsets 27 and 39 (`ifeq 46`, instruction indexes 21 and 25 in the report). I tested both polarities of the mutation by patching bytes in a scratch copy of the classes: (a) *skipping the shortcut* (what PIT's survival means: always go to the loop): an empty list yields `true` from the empty loop, a non-empty one runs the real check, so equivalent. (b) the opposite polarity (never jump at offset 39, i.e. `all` returns `true` for every non-empty list): this one is *not* equivalent, my probe then returns `AmountTooLargeException` instead of `IllegalArgumentException` for "oversized line, then foreign line", and test `a line in another currency is refused before any amount is looked at` (cart 1 and 3) fails on it. So the currency order of D-42 is really pinned, and the two survivors are the benign polarity. Holds.
- **`Percentage.getScale`.** Carried over, untouched: the getter is only used in an error message of `init`. Not part of this request.
- **Raw score.** 61/75 = 81.3 percent against 98.0 percent at story 2; the fall is the 12 equivalent mutants the new code introduces (10 intrinsics, the dead body, the stdlib shortcut pair). Over the 62 non-equivalent mutants the score is 61/62 (98.4 percent), the one survivor being the carried `getScale`. See m4.

## Manual mutations of the exact calls (redone on a scratch copy, one at a time, reverted)

| Replacement | Failing tests |
|---|---|
| `Math.addExact` -> `+` | 8: `EdgeAmountsTest` (code never hides, refused pricing changes nothing, total beyond range, total fits after discount, own refusal, lines fit alone but not together, order of lines) and `MoneyTest.adding stops exactly...` |
| `Math.subtractExact` -> `-` | 1: `MoneyTest.subtracting stops exactly...` (unreachable through pricing: discount <= subtotal) |
| `Math.multiplyExact` -> `*` | 2: `EdgeAmountsTest.a line beyond the money range is refused...`, `MoneyTest.multiplying by a quantity...` |
| `longValueExact()` -> `toLong()` | 2: `MoneyTest.taking a rate stops exactly...`, `...rounds half up before the result is checked...` |
| conversion -> rethrow of the raw exception | 13 (every test asserting `AmountTooLargeException`) |
| total as `subtotal + fee - discount` | 1: `EdgeAmountsTest.a total that fits after the discount is accepted although subtotal plus fee does not` (an `AmountTooLargeException` where a price is expected) |

All six match the Developer's table. I added further mutants the plan left to PIT, all killed: half-up `>=` -> `>` (4 tests), `require(minorUnits >= 0)` removed or `> 0` (1 / 5), `require(rate.numerator >= 0)` removed or `> 0` (1 / 3), `quantity > 0` -> `>= 0` (4), unit price check removed or `> 0` (1 / 5), fee check removed or `> 0` (2 / 12), promotion minimum check removed or `> 0` (1 / 12+), currency pre-pass removed (1), `all` -> `any` (5). No mutant survived.

## Findings

### Blocking
- none.

### Major
- none. Every consumer-visible behavior of the diff traces to a document or decision: negative inputs (A7/A8, D-37), the typed refusal (A3, A10, D-38, D-43, ADR-0003), scale (A11/A12, D-39), currency before amounts (D-42), negative operand of `times(rate)` (D-44). The two things the Developer lists as not decided (`Money(Long.MIN_VALUE)` buildable, `Money.times(Int)` signed) are not reachable through `PriceCart` and do not change a priced result.

### Minor
- **[m1] The exception message is built on every call, and carries the operand values** — `Money.kt:12`, `:17`, `:21`, `:36`; angle: debt. `exactly("$this + $other") { ... }` evaluates the template before `exactly` runs, so a `Money.toString` x 2 and a concatenation are paid on every `plus`, `minus`, `times`, success included. Measured on the compiled classes: about 110 ns per `plus` (5M additions in about 600 ms), against about 1 ns for a bare `addExact`. Harmless for a cart (a few microseconds), but a surprise in the one path the money zone exercises most. Also, the text names the two operand values while D-43 and `answers.md` say the message "does not name the amount": read narrowly (it does not say *which* of subtotal/discount/fee/total) the code complies, as the plan intends; nobody pins the text. Recommendation: pass the operation as a lambda or build the message in the `catch` only; decide with a person whether operand values may appear in a message (they are order amounts).
- **[m2] The Developer's survivor count is off** — `developer-1.md`; angle: debt. The note says 9 null-check mutants and "14 survivors": the report has 10 intrinsics, 13 SURVIVED and 1 NO_COVERAGE (the dead `exactly` body). The conclusions are right; correct the figures so the next reader can reconcile with `target/pit-reports/mutations.xml`.
- **[m3] `plan.md` is not brought up to date, and still carries a wrong figure** — `.plans/in-progress/edge-amounts/plan.md` sections 1, 3, 5, 8, 9, 10. All seven step boxes are still `[ ]`, sections 8 (deviations), 9 (self-review) and 10 (follow-up) are "(empty)", and the plan says "the 54 existing tests". The Developer's note is right and the plan is wrong: before this work there were **37** tests (`PriceCartTest` 15, `ApplyPromotionTest` 19, `MoneyTest` 3; verified at `bbdca93`) and 35 test-cases, now 62 and 60; none of the 37 was edited (0 deleted lines under `src/test`). The figure may come from a miscount of tests plus test-cases; there is no deviation from it. Recommendation: tick the steps, correct "54" to 37, put the Developer's self-review and follow-ups in sections 9 and 10, so the plan stays the persistent record.
- **[m4] No mutation baseline for a person to accept** — `docs/technical/invariants.md` INV-006 (unchanged by design); angle: debt. Score fell from 98.0 to 81.3 percent for equivalent-mutant reasons only (see above); a threshold of the raw score would punish this correct code, and the intrinsics and the stdlib shortcut will recur at every Kotlin `BigInteger` or `inline` use. Not a defect of the diff. For the person who sets the threshold: record 81.3 percent raw (61/62 non-equivalent) as the baseline, and consider excluding `Intrinsics.check*` calls from `VoidMethodCallMutator` in the PIT config.

## Checks not performed

- Linter / formatter: none configured (not available, not skipped).
- The repository-level checks outside `examples/meal-delivery-cart` (`validate-skills.py`, `check-glossary.sh`) are out of the review's scope.
- `docs/business` has no glossary file in this project; vocabulary was judged against `decisions.md` and the PRD only ("amount too large", "invalid input", "fee line" are the PRD's words and are used consistently by the 25 test-cases).
- Equivalence of A1 against the previous implementation was shown by the oracle (the old code is exact wherever it did not overflow and the input is non-negative, and the 37 unchanged tests are green), not by running the old code side by side.

## Positive notes

- The boundary tests are written as pairs on either side of the range (`max` accepted, `max + 1` refused) for every exact call and for the narrowing; this is why every manual mutation of an exact call, which PIT cannot see, is killed, and by the intended test.
- Placement follows the architect exactly: the typed refusal lives in `Money` only, `domain.pricing` has no catch or clamp (its only addition is the D-42 currency pre-pass), the order `subtotal - discount + fee` is pinned by a test that fails when swapped.
- Rounding stays single and in `domain.money`: one half-up on the whole product, narrowed after the rounding (`money-rate-rounds-before-narrowing` pins a share of `max - 0.5` and `max + 0.5`).
