# Brief: edge cases, blank member ids and the decliner writing back

- Request type: prompt (cites the PRD)
- Slug: edge-ids-and-decliner
- Iteration counter: 0
- Iteration limit: 5
- Delegation: the human delegated every decision (answered-by-delegate)
- A single story: the Product Owner does not cut it

## Objective

Implement `docs/product/prd/connection-requests-edge-ids-and-decliner.md` (status ready) on top of the built `connections` module.

## Acceptance criteria

Requirements 1 to 8 of that PRD, section 5. Decisions: `docs/business/decisions.md` (D-1 to D-32 and the answers to this PRD, recorded in the PRD itself). Out of scope, not decided: a non-blank id that names no known member (D-15), a blank *request* id, concurrency (another request).

## Context

Code: `src/connections/`, tests in `tests/connections/`, business test-cases in `docs/business/test-cases/connections/`. Architecture: ADR-0001, `docs/technical/invariants.md`. Plans and notes of the previous requests: `.plans/done/connection-requests/`.

## Carried over (open_majors of the previous requests)

- After A->B is declined, B->A is accepted by the code; no document decided it. This PRD decides it (requirements 5 to 8): the plan must cover it, and the mutation survivor at `domain/send-rules.ts:29` (`r.sender === c.sender` replaced by `true`) should be killed by it.
- Reads are unrestricted (D-24, deferred by decision; not part of this request).

## Answers

(none yet)
- Orchestrator, delegate: the Architect's change of the result shape of getPairState, listPendingRequests and eraseMember (they can now reject with `blank-member-id`) is accepted (the contract break is real but no consumer exists outside the module's tests). It is a role-file escalation case the Architect decided itself; recorded in RUN-NOTES.md.
