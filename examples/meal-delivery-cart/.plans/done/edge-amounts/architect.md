---
role: architect
status: done
structure: decided
reasons:
  - "No costly decision: ADR-0001/0002, INV-001..004 and the public signatures stay intact. Cheap choices recorded below and in ADR-0003 (additive: a typed exception, wide intermediate)."
---

# Architect note: edge cases on amounts

## Answers to the three questions

- **(a) ADR-0002 intact: yes.** `Money` stays `Long` minor units. Widening only the intermediate `minorUnits x numerator` (and dividing half up once) is an implementation detail inside `Money.times(Percentage)`; nothing wide is stored or exposed. ADR-0002 already named `Math.*Exact` as the overflow guard and reserved the caller-visible behavior, which ADR-0003 now settles. The widened product is at most about 8.5e37 (subtotal < 2^63, numerator <= 10^18 since the rules cap the rate at 100 percent), under 2^127, so 128 bits suffice; and because the rate is at most 100 percent, the quotient always fits a `Long`. A12 holds for every accepted scale.
- **(b) New refusal: a new public type, not a broken contract.** `AmountTooLargeException` (in `domain.money`, extends `ArithmeticException`). `PriceCart.price(cart, rules, code): Price` keeps its signature and return type. The old behavior (raw `ArithmeticException`) was never a documented contract (D-30 reserved it), and the subclass is still caught by any caller catching `ArithmeticException`. It is told apart from `IllegalArgumentException`, which stays the refusal for quantity zero, rate out of range, and now negative inputs (A3). What would have broken the contract, and is rejected: a sealed result type replacing the exception.
- **(c) INV-003 allows `BigInteger`, no amendment.** The rule bans `Double`, `Float` and `BigDecimal` only (statement and `ArchitectureTest` set); `java.math.BigInteger` is exact, integer and in the JDK, so INV-001 also holds. ADR-0002's reason to reject `BigDecimal` (invites unrounded values) does not apply. Rounding stays in `domain.money` (INV-002); do not use `BigInteger` rounding modes. `Math.multiplyHigh` with a manual 128-bit division is an equally valid choice; the Planner picks, `BigInteger` is simpler.

## Where each check lives (cheap to reverse)

- **Negative quantity, negative unit price (A7)**: `CartLine.init`, `require` (`IllegalArgumentException`), next to quantity zero. `Money` itself stays signed (generic, `minus` needs it).
- **Negative fee, negative promotion minimum (A8)**: `PricingRules.init`, `require`, next to the rate and currency checks. A rate below 0 is already refused there.
- **Amount too large (A2, A4, A10)**: in `Money` only: `plus`, `minus`, `times(Int)`, `times(Percentage)` throw `AmountTooLargeException`; `domain.pricing` adds no catch, so subtotal, discount, fee line and total are all covered. Mixed currencies stay `IllegalArgumentException`.
- **A9**: follows from A7/A8 and rate <= 100 percent (discount <= subtotal); no extra check.
- **A5, A1**: `price` is pure and builds a new `Price`; unchanged. Valid inputs give identical results.

## For the Planner

- Mutation gap: default PIT mutators do not touch `Math.*Exact`; guard sums with boundary tests (`Long.MAX_VALUE`, one over) on each operation, and on the widened product at scales 15 and 18.
- Sensitive zone (`domain.money`, `domain.pricing`): the human has approved the behavior through D-37 to D-39; the structure above needs no further approval.
- ADR-0003 written; the harness engineer may leave the invariants as they are.
