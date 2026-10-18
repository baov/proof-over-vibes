# Brief: edge cases, simultaneous operations

- Request type: prompt (cites the PRD)
- Slug: edge-concurrency
- Iteration counter: 0
- Iteration limit: 5
- Delegation: the human delegated every decision (answered-by-delegate)
- A single story: the Product Owner does not cut it

## Objective

Implement `docs/product/prd/connection-requests-edge-concurrency.md` (status ready) on top of the built `connections` module: simultaneous operations on the same pair of members behave as one of the two sequential orders.

## Acceptance criteria

Requirements 1 to 6 of that PRD, section 5. Decisions: `docs/business/decisions.md` (D-1 to D-36). Out of scope: how fast it is; non-blank unknown ids (D-15).

## Context

Code: `src/connections/` (the store port, the in-memory store, the use cases), tests in `tests/connections/`, business test-cases in `docs/business/test-cases/connections/`. Architecture: ADR-0001, `docs/technical/invariants.md`. Plans and notes of the previous requests: `.plans/done/`. The operations are asynchronous (D-21).

## Carried over (open_majors of the previous requests)

None. Minor items still open from earlier reviews: the Vitest 4.x pin and the mutation threshold await a human; the `EraseResult` type is not re-exported by `index.ts`.

## Answers

(none yet)
