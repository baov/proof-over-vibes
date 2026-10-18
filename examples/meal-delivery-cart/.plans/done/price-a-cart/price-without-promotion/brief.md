# Brief: price a cart, story 1 (price-without-promotion)

- Request type: prompt (feature "price a cart", brief.md of the parent folder)
- Story: 1 of 2, see ../stories.md ("Story 1"); its acceptance criteria are those of that section
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
