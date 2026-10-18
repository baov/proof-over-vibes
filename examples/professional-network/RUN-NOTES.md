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
