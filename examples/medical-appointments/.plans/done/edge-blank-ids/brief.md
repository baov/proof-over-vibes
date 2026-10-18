# Brief: edge case, blank identifiers

- Request type: prompt (cites the PRD)
- Slug: edge-blank-ids
- Iteration counter: 0
- Iteration limit: 5
- Delegation: middle way (cheap-to-reverse questions answered by the orchestrator with the role's recommendation, `answered-by-delegate`; product rules and costly choices go to the human)
- A single story: the Product Owner does not cut it

## Objective

Implement `docs/product/prd/book-a-slot-edge-blank-ids.md` (status ready) on top of the built booking module.

## Acceptance criteria

The requirements of that PRD, section 5. Decisions: `docs/business/decisions.md` (D-1 to D-35). Out of scope, not decided: simultaneous booking (another request).

## Context

Code: `src/main/java/io/example/medical`, tests in `src/test/java`, business test-cases in `docs/business/test-cases/book-a-slot/`. Architecture: ADR-0001, `docs/technical/invariants.md`. Earlier work: `.plans/done/`. Harness: `bash tools/harness/run_all.sh [--with-mutation]`; Maven is not on the PATH (`tools/harness/_maven.sh`), offline `-o`.

## Carried over (open_majors of the previous requests)

None. Minors still open: a `null` patient stored in a booking makes every later booking throw (identifiers were deferred, D-22: this request is where that gets decided); no mutation baseline is recorded (a human decision).

## Answers

(none yet)
