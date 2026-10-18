# Brief: edge cases, amounts (negative, too large, rate scale)

- Slug: edge-amounts

## Objective

Implement `docs/product/prd/price-a-cart-edge-amounts.md` (status ready) on top of the built pricing: negative inputs refused, an amount beyond the money range refused as 'amount too large', and every accepted rate scale pricing correctly.

## Acceptance criteria

Requirements A1 to A12 of that PRD, section 5. Out of scope: blank codes and concurrency (another request).

## Carried over (open_majors of the previous requests)

- Scales 10 to 18 are accepted but a valid rate throws from about 922 EUR at scale 15, and from 92 minor units at scale 18 (intermediate overflow in subtotal x numerator). This request settles it (A11, A12).
- Negative quantity, unit price, fee and promotion minimum are accepted (and negative subtotals round wrongly). This request settles it (A7 to A9).
- Overflow reaches the caller as a raw ArithmeticException. This request settles it (A2 to A4, A10).
- Minors: the default PIT mutators do not mutate `Math.*Exact`, so the exactness of the sums is protected by behavior tests only; the survivor `Percentage.getScale`; `Percentage(10,2) != Percentage(100,3)` so two rules holding the same 10 percent compare unequal (not part of this request unless a PRD requirement needs it).
- Request type: prompt (cites the PRD)
- Iteration counter: 0
- Iteration limit: 5
- Delegation: middle way (cheap-to-reverse questions answered by the orchestrator with the role's recommendation, `answered-by-delegate`; product rules and costly choices go to the human, `answered`)
- A single story: the Product Owner does not cut it

## Context

Code: `src/main/kotlin/io/example/mealcart`, tests in `src/test/kotlin`, business test-cases in `docs/business/test-cases/price-a-cart/`. Architecture: ADR-0001, ADR-0002, `docs/technical/invariants.md`. Earlier work: `.plans/done/price-a-cart/` (the Reviewers' reports are not archived: their open majors are quoted in each brief of that folder). Decisions: `docs/business/decisions.md` (D-1 to D-36, then the entries added for these PRDs). Harness: `bash tools/harness/run_all.sh [--with-mutation]`; Maven is NOT on the PATH (`tools/harness/_maven.sh`), offline `-o`. Kotlin 2.2.0, JUnit's `@Test` with kotlin.test assertions. The money zone (domain.money, domain.pricing) is a declared sensitive zone.

## Answers

(none yet)
