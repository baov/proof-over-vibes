# Brief: connection requests, story 2 (decline-and-withdraw)

- Request type: prompt (feature "connection requests", brief.md of the parent folder)
- Story: 2 of 2, see ../stories.md ("Story 2"); its acceptance criteria are those of that section
- Depends on story 1 (ask-and-accept) being merged first
- Iteration counter: 0
- Iteration limit: 5
- Delegation: the human delegated every decision (answered-by-delegate)
- Decision log: docs/business/decisions.md (D-1 to D-14 apply)
- PRD: docs/product/prd/connection-requests.md
- Architecture: docs/technical/adr/0001-*, architect note ../architect.md
- Harness: docs/technical/invariants.md; run `npm run harness` before each commit
- Open and NOT decided (ask, do not choose): member id validity, concurrency, a decliner sending a request back; any other behavior a caller would see that neither the stories nor the decision log settle
- Carried over: see the section below

## Answers

(none yet)

## Carried over (from story 1, review 1: GO, open_majors)

- M1: a request id from the id generator that already exists silently replaces the stored request (saveRequest overwrites). No decision says what a collision must do. Plan its fix or ask.
- M2: getPairState and listPendingRequests take no acting member: any caller can read any pair or member's pending list. No document says who may ask. Ask.

Minor items to take along: `pair-state.ts` uses the last request of the pair (valid for one request per pair): apply D-12 here and comment it; the survivor `domain/send-rules.ts:21` (`r.state === "pending"` replaced by `true`) should be killed by declined and withdrawn cases; the Vitest 4.x pin (commit 8a0ce23) awaits a human decision.
