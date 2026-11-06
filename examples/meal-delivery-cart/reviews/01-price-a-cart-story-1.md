---
role: reviewer
status: escalate
verdict: GO
reasons:
  - gauntlet green (tests, INV-001..005, mutation critical 91.7%), no blocking finding, 2 major findings (below the 3 that make a NO-GO)
  - escalate: the diff creates and touches the sensitive zone "Money computation and rounding" (domain.money, domain.pricing); a person must read this diff
severity: major
open_majors:
  - Negative quantity, negative unit price and negative fee are accepted and produce a negative subtotal/total (e.g. 1 x -500 with fee 250 gives total -250); no document settles it (D-30 is "reserved", answered-by-delegate)
  - Overflow surfaces to the caller as a raw ArithmeticException("long overflow") from PriceCart.price; ADR-0002 settles detection, not what the caller sees; D-30 reserved, untested
---

# Pre-merge review: price a cart, Story 1 (price-without-promotion), n=1

**Verdict: GO** (status `escalate`, sensitive zone)
**Date**: 2026-10-18. **Base**: 9103c58..a43f5c4. **Scope**: `examples/meal-delivery-cart` only, 23 files, +474 lines (7 production files = 85 lines, 1 test class = 179 lines, 15 test-cases).
**Criticality**: critical. Signals: domain layer, money computation (sensitive zone, D-15), public signatures consumed later (Story 2, order handoff).

## Summary

Story 1 is implemented as planned: nine small commits, behavior-level tests, test-cases created with their tests, no deviation. The arithmetic of the sum, the fee and the total is well protected (my manual mutations are killed except where noted below). What is left is not a code defect against the plan but behavior a caller will see that nobody decided: negative amounts and overflow. Both were "reserved" by a delegate answer nobody read. They go into `open_majors`. The diff is in a sensitive zone: a person reads it before merge.

## Gauntlet

| Check | Result |
|-------|--------|
| Test suite | OK: 15 tests, 0 failures (run through the harness Maven, offline) |
| Lint / format | not available (no ktlint/detekt/spotless in `pom.xml`; shape thresholds skipped by D-19) |
| Harness invariants | OK: INV-001..004 exit 0 |
| Test-case bridge | OK: 15 covered_ok, 0 broken, 0 pending, 0 orphan (INV-005) |
| Mutation (critical) | 91.7% (11 killed / 12), no threshold set; one survivor `Money.kt:14` (see m1) |
| Test-cases touched | 15 read: all under `docs/business/test-cases/price-a-cart/` |

`bash tools/harness/run_all.sh --with-mutation` from the project folder: exit 0.

## Breaking attempts (scratch copy outside the repository)

Probes run through `PriceCart.price` (EUR rules, fee 250 unless noted):

| Input | Result |
|---|---|
| 1 x (100, qty `Int.MAX_VALUE`) | exact: subtotal 214748364700, total 214748364950 |
| 1 x (`Long.MAX`, qty 2) | `ArithmeticException: long overflow` |
| 1 x (`Long.MAX`, qty 1), fee 250 | `ArithmeticException` (overflow when the fee is added) |
| same, fee 0 | exact: total `Long.MAX` |
| `Long.MAX` + 1 across two lines | `ArithmeticException` |
| `Long.MIN` x -1 | `ArithmeticException` |
| qty -2 at 500 | subtotal -1000, total -750 (accepted) |
| qty -1 at 500, fee 250 | total -250 (accepted) |
| unit price -500; fee -250 | accepted; negative total / negative `feeLine` |
| `Int.MIN_VALUE` quantity | accepted, subtotal -2147483648 |
| +500 and -500 lines (net zero, non-empty) | fee line present, total 250 (consistent with D-32) |
| zero fee, non-empty cart | `feeLine` = 0, total = subtotal |
| empty cart with a fee in another currency | impossible: `PricingRules` refuses the fee at construction; with a valid fee: zeros, `feeLine` null |
| 1,000,000 lines | exact, fast |
| EUR line + JPY line; a single JPY line under EUR rules | `IllegalArgumentException` ("Amounts in different currencies"), no result |

No silent wrong sum: the arithmetic fails closed on overflow. The only wrong-looking results are the negative ones.

Manual mutations (the default PIT mutators do not touch `Math.*Exact`), run against `PriceCartTest`:

| Mutation | Outcome | Caught by |
|---|---|---|
| `plus`: `addExact` -> `subtractExact` | killed (7 tests) | subtotal, exposes-every-line, same-line-twice, total... |
| `plus` returns `this` (ignores other) | killed (7) | same |
| `plus` without currency check | killed (1) | `a line priced in another currency than the rules is refused` (the only test for this guard) |
| `times`: `multiplyExact` -> `addExact` | killed (7) | subtotal tests |
| `times` ignores quantity | killed (6) | subtotal, same-line-twice |
| subtotal ignores quantity (Pricing) | killed (6) | same |
| `minus` operands swapped (`other - this`) | killed (4) | total test |
| total drops the fee | killed (5) | total, fee-line, free-lines |
| fee line present on empty cart | killed (1) | empty-cart test |
| fee only if subtotal > 0 | killed (1) | `a cart of free lines still has the fee line` |
| discount = subtotal | killed (5) | discount-is-zero, total |
| `CartLine` guard removed | killed (1) | quantity-zero test |
| `minus`: `subtractExact` -> `addExact` | SURVIVED | nothing (discount is always 0) |
| `minus` ignores other | SURVIVED | nothing |
| total = subtotal + discount | SURVIVED | nothing |
| `plus`/`times` without overflow detection | SURVIVED | nothing (overflow reserved, untested) |
| `CartLine` guard `!= 0` -> `> 0` | SURVIVED | nothing (negative quantity reserved) |
| fold seed in the fee's currency | SURVIVED | equivalent mutant (fee currency == rules currency by construction) |

The three `minus`/discount survivors are one fact: in Story 1 the discount is always zero, so the subtraction cannot be observed through the entry point. The test `price.subtotal - price.discount + price.feeLine!!` compares to 2150 but with a zero discount a wrong `minus` still agrees.

## Findings

### Blocking
None.

### Major
- **[M1] Negative amounts accepted, negative total returned** — `domain/cart/CartLine.kt:7` (`require(quantity != 0)`), `domain/money/Money.kt` (no sign check), `domain/rules/PricingRules.kt` · angle: bugs / compliance
  Observation: a negative quantity, a negative unit price or a negative fee prices normally; a cart of one line at quantity -1 and a 250 fee gives a total of -250. The guard is written `!= 0`, not `> 0`, so the code looks like a decision to refuse zero and accept negatives, while the brief says "negative or overflowing amounts: ask, do not choose". D-30 only says "leave reserved", answered-by-delegate (a role recommendation relayed, nobody read it), so no human settled it. A caller (display, order handoff) can show or charge a negative total. The `CartLine` guard mutation `!= 0` -> `> 0` survives: nothing pins the current behavior.
  Recommendation: the next planner asks the human (refuse negative quantity, price and fee? allow credits/refunds as negative lines? floor the total?), then decides guard and test-case. Until then do not describe negative acceptance as a feature. Consider at least writing `quantity > 0` only after that decision.
- **[M2] Overflow: caller sees a raw `ArithmeticException("long overflow")`** — `domain/money/Money.kt:10,16,19` · angle: bugs / compliance
  Observation: ADR-0002 settles that overflow is detected with exact arithmetic and that "what the caller sees stays reserved". The choice of a JDK exception type escaping `PriceCart.price`, while every other refusal is an `IllegalArgumentException`, is consumer-visible and undecided; no test pins it (survivors: overflow check removed in `plus` and in `times`). Failing closed is the right default for money (no wrong price is ever returned), so this is not blocking.
  Recommendation: the next planner asks what the caller sees (same exception family as the refusals? a typed error?), then adds a test per path (line product, running sum, adding the fee).

### Minor
- **[m1] Mutation survivor `Money.minus` (currency check) and unobserved arithmetic of `minus`** — `domain/money/Money.kt:13-15` · angle: bugs. Position: not a consumer defect today (unreachable through `PriceCart`: subtotal, discount and fee line share the rules' currency), but `minus` is public API of the money zone and its arithmetic and guard are protected by nothing. Do not remove the survivor with a test written only to kill it. Preferred: leave `minus` in place (Story 2 makes the discount non-zero and states the behavior at the entry point), and make the Story 2 plan list the three survivors (`minus` operator, operand order/guard, `subtotal - discount`) as to be killed by a discount test; if Story 2 slips, remove `minus` rather than keep unprotected money code. Adding a direct `Money` test class now is also acceptable but is a human call (sensitive zone, outside the plan).
- **[m2] `Money` public API (`plus`, `minus`, `times(Int)`, `zero`)** — `Money.kt` · angle: debt. Position: acceptable. ADR-0002 makes `Money` the public type; the operators are the minimal surface needed, and `times(Int)` ties the quantity type to `Int` (documented in the plan). Only `plus` and `times` are exercised, indirectly. Flag for Story 2: any new operator (percentage, rounding) must live in `domain.money` (INV-002).
- **[m3] Nullable `feeLine: Money?`** — `domain/result/Price.kt:6` · angle: compliance. Position: acceptable and settled: D-31 and criterion 13 say "absent (not zero)"; a nullable is the direct reading. Cost: every caller must null-check (the test already uses `!!`). Revisit only if Story 2 adds more optional lines.
- **[m4] `Cart` has no `equals`/`toString`; the mixed-currency error does not name the line** — `domain/cart/Cart.kt`, `Money.kt:23` · angle: debt. Two equal carts are not equal and log as `Cart@60099951`; a rejected cart gives "Amounts in different currencies: EUR and JPY" without saying which line. Low cost to fix, no risk to leave.

## Developer's "Behaviors added", positions

- Nullable `feeLine`: accepted (m3), covered by D-31.
- Negative quantity accepted: not accepted as a silent choice; it is M1 (and extends to negative price and fee).
- `ArithmeticException` on overflow: fail-closed is right, the visible type is undecided: M2. The developer's claim that D-30 and D-31 cover these is true only in the sense that they were left open.
- Public API of `Money`: accepted (m2).
- Entry point `object PriceCart`, `Cart` defensive copy, `PricingRules` without defaults: consistent with the plan and the architect note; no finding.

## Checks not performed

- Linter/formatter: none configured, not run.
- Mutation baseline: none recorded (no threshold yet, human decision, INV-006); the 91.7% score is informative. I did not re-run PIT with extra mutators on `Math.*Exact`; I replaced it by the manual mutations above.
- Security angle: no input boundary, secret, dependency or I/O in the diff (pom unchanged); nothing found. Concurrency (two operations on one cart): the pricing is pure over a copied list, the business meaning stays reserved by the PRD.
- Test-case `status`/priority wording was read against the glossary-less decision log; no business glossary file exists to check vocabulary drift.

## Positive notes

- Tests assert behavior through the entry point and read the amount a caller reads (`minorUnits`); the `a43f5c4` fix was a real gap, not a mutant-killer.
- The arithmetic of subtotal, fee and total is genuinely protected: 12 of 18 manual mutations die, and the 6 survivors map to reserved or equivalent cases, which the developer's note predicted (the blind spot on `Math.*Exact`).
- Every test-case carries a source and a precise `automated_test`; INV-005 clean on the first delivery.
