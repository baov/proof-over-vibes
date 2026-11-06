---
role: reviewer
status: escalate
verdict: GO
reasons:
  - gauntlet green (37 tests, INV-001..005, mutation critical 98.0%); no blocking finding; 1 new major finding (below the 3 that make a NO-GO); rounding, cap, decision order, minimum and sums verified by hand and found correct
  - escalate: the diff touches the sensitive zone "Money computation and rounding" (domain.money, domain.pricing); a person must read this diff before merge
severity: major
open_majors:
  - Scale 0..18 is accepted (D-35) but `subtotal x numerator` is computed in a Long: a valid 10 percent rate at scale 15 overflows from a subtotal of about 922 EUR, at scale 18 from 92 minor units, and the caller gets a raw ArithmeticException at pricing time although the discount itself would fit. No document says which scales are usable, nor what the caller sees
  - (carried over, story 1, still open) Negative quantity, unit price and fee are accepted and give a negative total; D-30 only reserved it. Story 2 adds one more surface: a negative promotion minimum is accepted by the rules
  - (carried over, story 1, still open) Overflow reaches the caller as a raw ArithmeticException; ADR-0002 settles detection, not what the caller sees; this story adds a second place (`subtotal x numerator`), see the first line
---

# Pre-merge review: price a cart, Story 2 (apply-a-promotion), n=1

**Verdict: GO** (status `escalate`, sensitive zone)
**Date**: 2026-10-18. **Base**: fad5f97..aba2313. **Scope**: `examples/meal-delivery-cart` only, 31 files, +641 / -11 (7 production files, about 70 lines; 2 test classes, 284 lines; 21 test-case files).
**Criticality**: critical. Signals: domain layer, money computation and rounding (sensitive zone), public signatures consumed by callers (`PriceCart.price`, `PricingRules`, `Price`, `Percentage`).

## Summary

Story 2 is implemented as planned, in nine small commits with behavior tests and a test-case per behavior. The arithmetic is right: I checked the rounding, the cap, the decision order, the minimum and the sums against an independent exact reference over about 63,000 rounding cases and 60,000 whole-price cases, with no mismatch and no silent wrap. The tests catch every rounding mutation I tried. What remains is a behavior a caller will see that nobody decided: the scales the type accepts (up to 18) cannot be used with ordinary amounts, because the intermediate product overflows a Long. That is one new major (open at the GO), on top of the two story 1 majors that stay open. The diff is in a sensitive zone: a person reads it before merge.

## Gauntlet

| Check | Result |
|-------|--------|
| Test suite | OK: 37 tests, 0 failures (`ApplyPromotionTest` 19, `MoneyTest` 3, `PriceCartTest` 15; run in a scratch copy and by the mutation run) |
| Lint / format | not available (no linter in `pom.xml`; same as story 1) |
| Harness invariants | OK: INV-001..004 exit 0 |
| Test-case bridge | OK: 35 test-cases, 35 covered_ok, 0 broken, 0 pending, 0 orphan |
| Mutation (critical) | 98.0% (48 killed / 49 generated), no threshold set. One survivor: `Percentage.kt:7`, `getScale` returns 0 |
| Test-cases touched | 21 read (all 20 new and the edited `no-discount-without-promotion`); they match Story 2 and decisions D-33..D-36, none invents a term |

Full command: `bash tools/harness/run_all.sh --with-mutation`, exit 0.

## Verification by hand (scratch copy outside the repository, nothing written in the project)

- **Rounding.** `Money.times(Percentage)` compared with an exact BigInteger half-up reference (`floor((2 s n + d) / 2d)`): scales 0 to 18, rates 0, 1, d/2, d, d-1, d/10, d/3, 5, 125 and 60 random per scale, subtotals 0, 1, 2, 9, 10, 99, 100, 101, 999, 1000, 1009, 1010, 1011, 9e9, Long.MAX/2, Long.MAX plus 60 random. 62,986 results, 0 mismatch. Exhaustive: scales 0..4, every numerator 0..10^scale, subtotals 0..300 (3,345,916 results), 0 mismatch. Exact halves round up. Rate 0 percent gives 0, rate 100 percent gives the subtotal.
- **Overflow, silent or not.** 37,961 of the cases above overflow: all of them throw ArithmeticException, none returns a wrapped value, and none throws when `subtotal x numerator` fits a Long (no spurious overflow). Detection is sound. See M1 for what it costs.
- **Cap.** In the same runs and in 60,000 whole-price cases (EUR 2 digits, JPY 0, KWD 3), the discount is always between 0 and the subtotal, so the food total after discount is never below zero. The missing `min()` clamp is justified for non-negative inputs.
- **Whole price.** Over 60,000 random carts, fees, minimums, rates and codes (null, valid, unknown, empty cart, fee 0): `subtotal`, `feeLine`, `discount`, `total == subtotal - discount + fee` (the sum of the displayed lines), reason and discount all match an independent model. 0 inconsistent. A 100 percent rate with a fee gives total == fee, never below it.
- **Decision order and minimum.** no code, then unknown code (also when the rules hold no promotion), then below minimum, then apply. The minimum is compared with the exact subtotal (`subtotal < minimum`), not with the discount; equal to the minimum applies.
- **Do the tests catch broken arithmetic?** Manual mutations of `divideHalfUp`, `times` and `Pricing.kt`, each run against the real suite (27 mutations):
  - KILLED: `>=` to `>`; ceil (`remainder > 0`); floor (never up); always up; half-even; `2r + 1 >= d`; `2r >= d - 1`; `3r >= d`; `remainder >= divisor`; `quotient + 2`; denominator / 10; numerator + 1; `compareTo` reversed; `compareTo` guard removed; minimum `<` to `<=` and to `>`; unknown-code / minimum order swapped; code `equalsIgnoreCase`; code trimmed; discount also taken off the fee (total and displayed fee line); per-line rounding instead of rounding once; minimum compared with the discount.
  - SURVIVED: `Math.multiplyExact`, `addExact`, `subtractExact` replaced by plain `*`, `+`, `-` (silent wrap on overflow; the known PIT blind spot, and overflow behavior is reserved, so no test states it); `dividend % divisor` rewritten as `% divisor % divisor` (equivalent mutant).
  - So the rounding is protected by behavior tests (the exact-half case 1010 at 5 percent, the 99.9 percent case on 1, the three-lines case, 1 percent of 10). The sums are protected by the 2150 / 215 / 250 / 2185 test, which also kills `minus` -> `plus` style mutants. Only the overflow exactness is unprotected, as the plan said.

## Findings

### Blocking
None.

### Major

- **[M1] Scales 15 to 18 (and part of 10 to 14) are accepted but cannot price ordinary amounts; the caller gets a raw ArithmeticException** — `Money.kt:23` (`Math.multiplyExact(minorUnits, rate.numerator)`), `Percentage.kt:8-11` (scale 0..18) · angle: bugs and decision (D-35 rationale)
  Observation: D-35 accepts scale 0..18 "because 10^scale fits a Long", but the product `minorUnits x numerator` is what must fit. A valid 10 percent rate (`Percentage(10^(s-1), s)`) prices 2000 minor units up to scale 12, throws from a subtotal of 100,000 at scale 15 (limit about 92,233 minor units), and already throws on 2000 at scale 17 and 18 (limit about 922 and 92). I ran it: `PriceCart.price` throws `ArithmeticException` for scale 15 / 100,000, scale 17 / 2000, scale 18 / 2000. The result (200) fits a Long easily, so this is an implementation limit, not a real overflow. The exception comes at pricing time, from rules that were accepted at construction, which sits badly with D-28 ("no cart is priced with invalid rules"). The plan filed it under the reserved "overflow" and the developer note says "no consumer-visible behavior lacks a document": no document says which scales are usable.
  Consequence: a rules author who picks a fine scale (the type invites it) sees a working price in tests with small amounts and a crash in production with a normal cart. It is also a behavior a consumer sees that no document or decision settled, hence major.
  Recommendation (for the next planner to ask, not to decide here): either bound the scale to what the amounts can bear (the question is which bound and what happens above), or compute the product without the intermediate overflow (the result always fits), or state the usable envelope and the error in a decision. Add the test that states the chosen outcome at a high scale.

### Minor

- **[m1] A negative promotion minimum is accepted by the rules** — `PricingRules.kt:14-17` · angle: bugs. Only the currency of the minimum is checked. A negative minimum is always met; with a negative subtotal (also accepted, carried over) the discount is then negative and `divideHalfUp` rounds negatives wrongly (-50.55 gives -50, half up would give -51). Same class as the reserved negative amounts (D-30); no new decision taken, but fold it into the question the edge-case request will ask.
- **[m2] The overflow exactness of `Money` has no test** — `Money.kt:8,13,17,23` · angle: debt. Replacing `Math.*Exact` by plain arithmetic survives (see the mutation list). Expected until the overflow behavior is decided (M1, carried over); once it is, add the behavior test then.
- **[m3] The denominator at scale 18 is never exercised** — `ApplyPromotionTest.kt` (`a rate with a scale outside 0 to 18 is refused`) only builds `Percentage(1, 18)`. A change to the power-of-ten loop that breaks scale 16 to 18 would pass. It resolves with M1 (a test at the chosen bound).
- **[m4] Equal rates are not equal values** — `Percentage.kt`, `Promotion.kt`, `PricingRules.kt` (data classes). `Percentage(10, 2) != Percentage(100, 3)`, so two `PricingRules` holding the same 10 percent compare unequal. The developer listed it as "no decision needed"; no consumer is known to compare rules, hence minor. Worth a line in the next decision pass.

## Position on the Developer's points

- **Public `Money.compareTo`: accept.** The plan names it, it is the least code that gives the "not below" comparison, it refuses mixed currencies exactly like `plus` and `minus`, and it is consistent with ADR-0002. It is tested (`amounts of the same currency compare by value...`), and the mutations "reversed" and "guard removed" are both killed. It is visible only to Kotlin callers using `<`; no decision needed. (`Money` is not `Comparable`, so no sorting by accident.)
- **Survivor `Percentage.getScale`: accept, do not exclude it in `pom.xml`.** The developer's reading is right for production code (only the text of the refusal message reads it, and the message is not a contract). But `scale` is a public component of the type (`componentN`, `copy`, equals) and a caller can read it; an exclusion would hide a real getter and set a precedent. Leave it as the single recorded survivor; if a threshold is set later, one behavior test ("a rate keeps the scale it was built with") would state it without being a mutant-killing test. No action for this merge.

## Checks not performed

- No linter or formatter exists in the project. Concurrency and blank codes are reserved by the brief and were not reviewed as defects.
- No test-case exists for the public `Money.compareTo` alone (INV-005 does not require one).
- The architect note body is stale (it still says `Percentage` guards a non-negative numerator); D-36 settles it, and the brief says its body was not to be edited. Not a finding.

## Positive notes

- One rounding function, in `domain.money` only (INV-002), no `min()` clamp, no `Double`; the half-up line is protected by genuinely behavioral tests, and every rounding mutation I tried is killed.
- Decisions D-33..D-36 are applied to the letter (closed reasons in one field, optional promotion, exact-text match, rate bounds in the rules), and the exact-match test pins four near-misses.
- The story 1 minors were handled as asked: the non-zero discount test kills the `minus` and total mutants through behavior, and the `Money` API test covers the unreachable currency guard.
