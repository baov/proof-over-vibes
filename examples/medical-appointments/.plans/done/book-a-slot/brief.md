# Brief: book a slot

- Request type: prompt (cites the PRD)
- Slug: book-a-slot
- Iteration counter: 0 (for the feature; each story has its own counter in its subfolder)
- Iteration limit: 5
- Delegation: middle way. The Orchestrator answers cheap-to-reverse technical questions with the role's recommendation (`answered-by-delegate`); product bets and costly-to-reverse choices go to the human (`answered`).

## Objective

Implement the feature described by the PRD `docs/product/prd/book-a-slot.md` (status ready): a patient books a free slot of a practitioner; a taken, past, unknown or overlapping slot is refused. Pure domain behavior: no UI, no accounts, no payment; slots are preloaded.

## Acceptance criteria

The 12 requirements of the PRD, section 5. Its open questions (simultaneous booking of the same slot; empty or blank identifiers) are NOT decided: a role that meets one asks.

## Fixed by the human (stack, given in the request)

Java 21 (JDK 21), Maven (the Maven distribution under `~/.m2/wrapper/dists`, no `mvn` on the PATH; a Maven wrapper or the full path), JUnit 5. Everything else (structure, style, dependencies beyond these) is for `architect` to propose. The machine is offline-friendly: only artifacts already in `~/.m2/repository` can be used without a download; any other dependency or plugin (a mutation tool for instance) is a question for the human.

## Carried over

None (first request of the project).

## Answers

(none yet)
