# Brief: edge case, simultaneous bookings

- Request type: prompt (cites the PRD)
- Slug: edge-simultaneous
- Iteration counter: 0
- Iteration limit: 5
- Delegation: middle way (cheap-to-reverse questions answered by the orchestrator with the role's recommendation, `answered-by-delegate`; product rules and costly choices go to the human)
- A single story: the Product Owner does not cut it

## Objective

Implement `docs/product/prd/book-a-slot-edge-simultaneous.md` (status ready) on top of the built booking module: what the loser of a simultaneous booking sees.

## Acceptance criteria

The requirements of that PRD, section 5. Decisions: `docs/business/decisions.md` (D-1 to D-35). Out of scope: blank identifiers (another request), the speed of the product.

## Context

Code: `src/main/java/io/example/medical`, tests in `src/test/java`, business test-cases in `docs/business/test-cases/book-a-slot/`. Architecture: ADR-0001, `docs/technical/invariants.md`. Earlier work: `.plans/done/book-a-slot/` (the concurrency tests of story 2 deliberately do not inspect the loser). Harness: `bash tools/harness/run_all.sh [--with-mutation]`; Maven is not on the PATH (`tools/harness/_maven.sh`), offline `-o`.

## Carried over (open_majors of the previous requests)

None. Minors still open: the 500 ms decorator wait in the concurrency tests could let them pass without the lock on a very slow machine; the loser of a race currently sees TAKEN or OVERLAPPING in fact, pinned by no test; no mutation baseline (a human decision).

## Answers

(none yet)
