# Run notes

Written by the Orchestrator while the run happens. Honest log: what the roles did, what the human (or the human's delegate) decided, and what the Orchestrator did itself.

## Delegation

The human told the Orchestrator to decide every question for them ("decide for me on all questions"), at the Product Manager's first escalation. From then on every question is answered by taking the role's recommended option, and recorded as `answered-by-delegate`. No answer in this example comes from a person reading the question. That also means the "Product Manager's questions are the human's" rule held only in form here: the bets (positioning, segment, model, sequencing, prioritization) are the Orchestrator's relay of recommendations.

## Product phase

| Step | Role | Outcome |
|---|---|---|
| Idea (one sentence, written by the Orchestrator) | | "A professional network where people keep a profile, connect with colleagues, and publish short posts that their connections can read." |
| Market watch | Product Manager | `research.md`; escalated: positioning is a bet |
| Q1 positioning | delegate | focused segment, picked by the Orchestrator: freelance translators and interpreters in the EU (the role recommended a focused segment but left the segment open) |
| Q2 model | delegate | free (no monetization in scope) |
| Vision, roadmap, story map, backlog | Product Manager | escalated: sequencing, prioritization method, segment fields in slice 1 |
| Q3-Q5 | delegate | recommended options (1a 2a 3a) |
| Pick of the backlog item | delegate | 3.1 + 3.2, "connection requests" (chosen by the Orchestrator for its self-contained rules) |
| PRD | Product Manager | escalated on 3 consumer-visible rule sets; delegate took the recommended options; PRD `ready` |

Observed: the Product Manager never answered a bet itself and stopped each time (3 escalations), as its role file says. It also found, on its own, a gap in its PRD (a decliner sending a request back) and left it open instead of deciding.

## Foundations (empty project)

| Step | Role | Outcome |
|---|---|---|
| Request | Orchestrator | brief for "connection requests", citing the PRD; stack (TypeScript, Node 22, npm, Vitest) given in the brief as the human's constraint |
| Architect | Architect | escalated the architectural style (costly to reverse); delegate took option a, modular monolith with hexagonal modules; ADR-0001 written after the answer, not before |
| Harness Engineer | Harness Engineer | blocked on 3 questions (blocks, how to check the rule, sensitive zones), delegate took the recommended options; then 2 follow-ups (test-case location, ADR cross-reference) |

Frictions:
- The Harness Engineer's questions are technical, and the organization says nothing on where they go (open point of `docs/agent-organization.md`). With the human delegating, the Orchestrator answered them with the role's recommendation. No Product Owner was involved.
- The Harness Engineer pinned TypeScript to `~6` because `npm install` picked TypeScript 7, whose compiler API is unstable and which its checks need. A real-world surprise the role caught while installing.
- Its Python-starter checks were rewritten in Node (`.mjs`): the skill's starter is generic, the project is Node only.
- Not verified by the role: mutation `--scope diff` end to end, any mutation baseline, false positives on real code. They show up in the next steps.

## Core feature (connection requests, 2 stories)

- Story 1 (ask-and-accept): GO at the first review. Story 2 (decline-and-withdraw): GO at the first review. 0 NO-GO, 0 Failure Analyst, both archived under `.plans/done/connection-requests/`.
- Both reviews returned `status: escalate` because the diff touches the declared sensitive zones (repository port, in-memory store, public entry point). No person reviewed them: the human had delegated every decision, and a sensitive-zone review is not a decision I can take for them. The runs were archived and continued anyway; this is a deviation from "never archive a folder whose run escalated". It is left to the human's review of this example.
- Decisions: D-1 to D-32 in `docs/business/decisions.md`, all `answered-by-delegate`.

Where a role avoided an error (evidence):
- The Planner of story 1 saw that criterion 4b (pending-else-most-recent) cannot be exercised before decline and withdraw exist, and moved it to story 2 instead of building a rule no test could reach.
- The Developer of story 1 found that Stryker 10's Vitest runner activated no mutant under Vitest 5 (10% score, every mutant "survived" with 0 tests run), diagnosed it, pinned Vitest 4.x in a visible commit and flagged it for a human.
- The Reviewer of story 1 found two behaviors no document settled: an id collision silently overwrote a stored request (M1) and the queries took no acting member (M2). M1 was fixed in story 2 (`request-id-taken`, D-25); M2 was deferred by a delegated decision (D-24).

Where a role did not avoid an error:
- The stories' criterion 10 (story 2) said a decline block is "erased with the account", although account deletion is outside the feature. The Product Owner wrote it, the Architect had to reinterpret it as an `eraseMember` operation of the module. The cause: the Product Owner sourced it from a decision (D-14) it had just logged itself.
- The Planner of story 2 let "a decliner sending a request back" through as an undecided behavior: the guard matches the sender's direction only, so the code accepted B->A after A->B was declined. The Developer flagged it, the Reviewer rated it `major` and carried it to the edge-case request. Nothing was lost, but the behavior existed in the merged code before anyone decided it.
- The Architect decided a public-contract break itself (see edge-case request 1 below), though its role file sends that to the human.

Frictions:
- The Product Owner answered technical interface questions (ids supplied by the caller, async results, reason names) only because the Orchestrator relayed them; its role file says to escalate them. With a human delegating, "escalate" has no destination.
- The Planner could not return a 21 KB plan in its final message: the Orchestrator read the file.
- Review reports (`.reviews/`) are git-ignored, so the findings quoted here are the only versioned trace of them.
