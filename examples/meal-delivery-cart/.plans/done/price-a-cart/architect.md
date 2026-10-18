---
role: architect
status: done
structure: decided
reasons:
  - "Structure decided on the empty-project pass: hexagonal light (ADR-0001), Money(minorUnits: Long, Currency) with an exact decimal Percentage (ADR-0002). The stories add nothing costly: the checks below (rate bounds, quantity zero, rules value) are cheap to reverse and recorded here. One shape question goes to the planner: the typed reason a promotion did not apply."
---

# Architect note: price a cart

Final note. ADR-0001 and ADR-0002 are accepted and unchanged by the stories; no new ADR. No debt flagged: the project is empty.

## Context

- Small, money-heavy pure core: lines, one percentage promotion, one flat fee, one currency, half-up rounding to the smallest unit, every rule a parameter. No UI, persistence or I/O now. Roadmap: more fee lines, tax, tip, promotion variants, then order handoff (the first outside boundary).
- Stack fixed by the human: Kotlin 2.2.0, JDK 21, Maven, kotlin-test + JUnit Jupiter 5.12.2, offline, no new dependency.

## Structure (decided, see the ADRs)

- Hexagonal light (ADR-0001): `domain` (cart, money, rules, pricing, result) imports only the standard library; `application` (one pricing entry point) depends on `domain`; no port before order handoff.
- `Money(minorUnits: Long, Currency)`, `Percentage` as integer numerator over a power of ten, never `Double` (ADR-0002).
- Invariants in force: INV-001 dependency rule, INV-002 single rounding point, INV-003 no floating point, INV-004 purity. Sensitive zone: `domain.money` and `domain.pricing`.

## Cheap-to-reverse decisions

- **Rounding**: one half-up function in `domain.money`, from an exact `numerator/denominator`; discount and fee both go through it, nothing else rounds. Subtotal is an exact integer sum; the total is the sum of the already-rounded lines (R16).
- **Rules value**: one immutable `PricingRules` (currency, delivery fee, promotion: code(s), rate, minimum) passed as an argument to the pricing function. Built by its constructor, no builder, no default for any amount, rate, threshold or currency (R4, R6). The core reads no configuration; a configuration adapter is a later feature.
- **Rules validation (D-22, D-28, D-29)**: lives in the construction of `PricingRules` (its promotion part), which raises `IllegalArgumentException` through `require` when the rate is below 0 or above 100 percent (bounds inclusive). It is not in `Percentage`: a `Percentage` is a generic exact decimal that tax or tip may later take above 100 percent, so it only guards its own representation (non-negative numerator, valid scale). The same construction rejects an amount whose currency is not the rules' currency (R15). No cart is ever priced with invalid rules, since pricing takes a `PricingRules` that cannot exist in that state.
- **Quantity zero (R18, D-24)**: a `CartLine` refuses quantity zero at its construction (`require`, `IllegalArgumentException`), so a `Cart` can never hold one and pricing never sees it, with or without a code. Negative quantity and negative or overflowing amounts remain reserved (PRD section 6): the type allows the later choice, I do not decide it.
- **Line content (D-27)**: a line holds a unit price (`Money`) and a quantity only; its currency is checked against the rules at pricing time or by the cart, never stored twice.
- **Purity (R3, R5)**: pricing is a stateless function over an immutable `Cart` and `PricingRules`; no clock, randomness or I/O; it returns a new `Price` and never mutates the cart. Two simultaneous pricings cannot interfere. What "two operations on one cart" means for the business stays reserved.
- **Boundary**: `Cart` is a value-like input, `Price` a value object. No repository, no service named after one operation.
- **Vocabulary** follows the PRD: line, subtotal, discount, fee line, total, rules, promotion code.

## Question for the planner

The reason a promotion did not apply (R9, D-9, D-23) must come back in the result as a typed value, not a string. No document fixes its shape: the PRD and the stories say only "the reason stated in the result". Suggested, for the planner to settle with the stories: a result field holding either nothing (applied, or no code supplied) or a closed set of two reasons (unknown code, subtotal below the minimum), with unknown code winning when both hold (D-23). This is cheap to reverse while no caller exists; if the planner finds the stories leave a case open (for instance, what is returned when no code is supplied), it asks the product owner rather than deciding here.
