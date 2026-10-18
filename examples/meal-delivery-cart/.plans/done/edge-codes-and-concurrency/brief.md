# Brief: edge cases, blank codes and simultaneous pricing

- Slug: edge-codes-and-concurrency

## Objective

Implement `docs/product/prd/price-a-cart-edge-codes-and-concurrency.md` (status ready) on top of the built pricing: a blank or empty code, and several simultaneous pricings of one cart.

## Acceptance criteria

Requirements C1 to C9 of that PRD, section 5. Out of scope: negative and too-large amounts (another request).

## Carried over (open_majors of the previous requests)

None beyond the amounts request. Minors: the promotion code is matched by exact text (D-34); `Percentage(10,2) != Percentage(100,3)`.
- Request type: prompt (cites the PRD)
- Iteration counter: 0
- Iteration limit: 5
- Delegation: middle way (cheap-to-reverse questions answered by the orchestrator with the role's recommendation, `answered-by-delegate`; product rules and costly choices go to the human, `answered`)
- A single story: the Product Owner does not cut it

## Context

Code: `src/main/kotlin/io/example/mealcart`, tests in `src/test/kotlin`, business test-cases in `docs/business/test-cases/price-a-cart/`. Architecture: ADR-0001, ADR-0002, `docs/technical/invariants.md`. Earlier work: `.plans/done/price-a-cart/` (the Reviewers' reports are not archived: their open majors are quoted in each brief of that folder). Decisions: `docs/business/decisions.md` (D-1 to D-36, then the entries added for these PRDs). Harness: `bash tools/harness/run_all.sh [--with-mutation]`; Maven is NOT on the PATH (`tools/harness/_maven.sh`), offline `-o`. Kotlin 2.2.0, JUnit's `@Test` with kotlin.test assertions. The money zone (domain.money, domain.pricing) is a declared sensitive zone.

## Answers

(none yet)
