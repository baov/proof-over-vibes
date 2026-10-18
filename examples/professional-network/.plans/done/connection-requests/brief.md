# Brief: connection requests

- Request type: prompt
- Slug: connection-requests
- Iteration counter: 0 (for the feature; each story has its own counter in its subfolder)
- Iteration limit: 5
- Delegation: the human delegated every decision. A question is answered by the recommended option and recorded `answered-by-delegate`.

## Objective

Implement the feature described by the PRD `docs/product/prd/connection-requests.md` (status ready): a member sends a connection request to another member, who accepts or declines; the sender can withdraw. Pure domain behavior: no UI, no sign-in, no profile, no feed. Members are identified by an id.

## Acceptance criteria

The 15 requirements of the PRD, section 5, are the acceptance criteria. Its open questions (member id validity, concurrency, a decliner sending a request back) are NOT decided: a role that meets one asks.

## Fixed by the human (stack, given in the request)

TypeScript on Node 22, npm, Vitest. The project is empty: no code, no package file. Everything else (structure, style, dependencies beyond these) is for `architect` to propose.

## Carried over

None (first request of the project).

## Answers

(none yet)
