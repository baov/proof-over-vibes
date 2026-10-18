# Brief: price a cart, story 2 (apply-a-promotion)

- Request type: prompt (feature "price a cart", brief.md of the parent folder)
- Story: 2 of 2, see ../stories.md ("Story 2"); its acceptance criteria are those of that section
- Depends on story 1 being merged first
- Iteration counter: 0
- Iteration limit: 5
- Delegation: middle way (cheap-to-reverse questions answered by the orchestrator with the role's recommendation, `answered-by-delegate`; product rules and costly choices go to the human, `answered`)
- Decision log: docs/business/decisions.md
- PRD: docs/product/prd/price-a-cart.md
- Architecture: docs/technical/adr/0001-*, 0002-*, architect note ../architect.md (its front-matter and the ADRs are final; its body still reads as the old escalation note)
- Harness: docs/technical/invariants.md; bash tools/harness/run_all.sh [--with-mutation] before each commit; Maven is NOT on the PATH: tools/harness/_maven.sh, offline -o
- Base package: io.example.mealcart (pom.xml base.package and ArchitectureTest must change together)
- Open and NOT decided (ask, do not choose): negative or overflowing amounts; blank or empty identifiers and codes; two operations on one cart at the same moment; any other behavior a caller would see that neither the stories nor the decision log settle
- Carried over: none

## Answers

(none yet)

## Carried over (from story 1, review 1: GO, open_majors)

- Negative quantity, unit price and fee are accepted and give a negative total (1 x -500 + fee 250 -> total -250). D-30 only reserved it. RESERVED for a later edge-case request: do not decide it; if the plan touches it, ask.
- Overflow reaches the caller as a raw ArithmeticException; ADR-0002 settles detection, not what the caller sees; untested. Same: reserved for the edge-case request.

Minor items to take along: `Money.minus` is unprotected because the discount is always 0 in story 1 (three manual mutations survive: subtractExact -> addExact, minus ignoring its operand, total = subtotal + discount): this story's non-zero discount tests must kill them (behavior tests, not mutant-killing tests), or `minus` is removed; the survivor in `Money.minus` (currency guard) is unreachable through PriceCart; the default PIT mutators do not mutate `Math.*Exact` arithmetic, so only the behavior tests protect the sums.
