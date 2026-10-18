# Brief: book a slot, story 1 (book-and-never-double-book)

- Request type: prompt (feature "book a slot", brief.md of the parent folder)
- Story: 1 of 2, see ../stories.md ("Story 1"); its acceptance criteria are those of that section
- Iteration counter: 0
- Iteration limit: 5
- Delegation: middle way (cheap-to-reverse questions answered by the orchestrator with the role's recommendation, `answered-by-delegate`; product bets and costly choices go to the human)
- Decision log: docs/business/decisions.md
- PRD: docs/product/prd/book-a-slot.md
- Architecture: docs/technical/adr/0001-*, architect note ../architect.md
- Harness: docs/technical/invariants.md; tools/harness/run_all.sh before each commit; Maven at /Users/baovuong/.m2/wrapper/dists/apache-maven-3.9.11-bin/6mqf5t809d9geo83kj4ttckcbc/apache-maven-3.9.11/bin/mvn (see tools/harness/_maven.sh), run offline (-o) once dependencies are resolved
- Open and NOT decided (ask, do not choose): simultaneous booking of one slot, blank or empty identifiers; any other behavior a caller would see that neither the stories nor the decision log settle
- Carried over: none

## Answers

(none yet)
