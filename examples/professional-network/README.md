# Professional network: an example

A small TypeScript module, `connections` (a member asks another to connect; the other accepts or declines), built from a one-sentence idea by the roles and skills of this repository. Nothing here was written by hand except the idea, the briefs and these notes.

> Idea: "A professional network where people keep a profile, connect with colleagues, and publish short posts that their connections can read."

## What you get

| From | You get | Where |
|---|---|---|
| The idea | market watch (sourced or marked *unverified*), vision, roadmap, story map, backlog, a PRD for the picked feature, two edge-case PRDs | [`docs/product/`](docs/product) |
| The questions | 38 numbered decisions, each with a source | [`docs/business/decisions.md`](docs/business/decisions.md) |
| The code | the module, 88 behavior tests | [`src/connections`](src/connections), [`tests`](tests/connections) |
| The tests | 87 business test-cases, each naming its source and its automated test, checked by a bridge | [`docs/business/test-cases`](docs/business/test-cases/connections) |
| The architecture | two ADRs, turned into executable invariants | [`docs/technical`](docs/technical) |
| The checks | a harness (layers, shape, test-case bridge, serialization, mutation) | [`tools/harness`](tools/harness) |
| Each change | its plan, its notes, its metrics | [`.plans/done/`](.plans/done), [`.metrics/`](.metrics) |
| A bug | a diagnosis with a replayable proof, then a fix | [`.plans/done/bug-unrelated-members-connected`](.plans/done/bug-unrelated-members-connected) |

## What you would not have without the repository

- **Rules nobody invented.** Every behavior a caller sees (who may accept, what a second request does, which reason wins when two rules apply) traces to a PRD line or a numbered decision. The Planners and the Developers stopped and asked, round after round, instead of choosing; see [`RUN-NOTES.md`](RUN-NOTES.md).
- **Tests that are checked.** The mutation score (100% before the planted bug) says the tests catch changes; the bridge says every test belongs to a business case.
- **A bug found from a report alone**, proved by a replay, with a second symptom the diagnosis had missed found by the review.

## Where a role avoided an error, and where it did not

- Avoided: a Reviewer found that an id collision silently overwrote a stored request and that queries took no acting member (story 1 review); the fix came in story 2 (`request-id-taken`, D-25). A Developer found that the mutation tool activated no mutant under Vitest 5 and pinned 4.x in a visible commit.
- Not avoided: the planted regression passed the tests and the whole harness. Only the mutation score fell, and no threshold turned that into a failure. Also, the code accepted a request from a decliner back to the decliner's sender before any document decided it; a review caught it one story later.

Evidence for each, with the commits, is in [`RUN-NOTES.md`](RUN-NOTES.md).

## What the example does not show

- **No human in the loop.** The human delegated every decision, so all 38 are `answered-by-delegate` and none was read by a person. Every review ended `escalate` on the sensitive zones; nobody reviewed them.
- **No NO-GO.** Every review was a GO at the first pass, so the Developer and Reviewer loop and the Failure Analyst never ran.
- **One planted regression**, by design, and a small domain core: no storage, no network, no UI, no sign-in.
- **Roles not installed in a client**: each was started as a fresh agent that read its role file (see the notes).

## Run it

```bash
npm install
npm test               # 88 tests
npm run harness        # invariants and the test-case bridge
npm run mutation       # Stryker, about 90% (dead code left by the planted regression)
```
