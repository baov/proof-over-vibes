# Run notes

Written by the Orchestrator while the run happens. Honest log: what the roles did, what the human decided, and what the Orchestrator did itself.

## Delegation

Unlike the first example, the human chose the middle way here: the Orchestrator answers the cheap-to-reverse technical questions with the role's recommendation, and every bet of the Product Manager and every escalation of a role goes to the human. Entries in the decision log are `answered` (read by the human) or `answered-by-delegate` (Orchestrator's relay of a recommendation, nobody read it).

## Product phase

| Step | Role | Outcome |
|---|---|---|
| Idea (one sentence, written by the Orchestrator) | | "An online booking service for medical appointments where patients see a practitioner's free slots, book one, and cancel it." |
| Market watch | Product Manager | `research.md`; escalated 3 bets |
| Positioning, country, nature | human | narrow and simple; EU (GDPR); learning example (price model out of scope) |
| Vision | Product Manager | written; escalated success measures, first slice, horizons, prioritization |
| Success, first slice, horizons, prioritization | human | the three measures; see/book/cancel for one practitioner; Now = skeleton + practitioner availability (not the PM's recommendation); MoSCoW |
| Roadmap, story map, backlog | Product Manager | written, nothing picked |
| Backlog pick | human | F2.1 + F2.2, "book a slot" |
| PRD | Product Manager | escalated 3 rules |
| Rules | human | past slot refused; several bookings per patient but no overlap (not the PM's recommendation); re-booking an own slot refused |
| PRD | Product Manager | ready; two boundary conventions stated by the PM without source (back-to-back slots do not overlap, a slot starting exactly now can be booked), flagged, not asked: nobody read them |

## Foundations (empty project)

| Step | Role | Outcome |
|---|---|---|
| Request | Orchestrator | brief for "book a slot", citing the PRD; stack (Java 21, Maven, JUnit 5) given as the human's constraint |
| Architect | Architect | escalated the architectural style; the human chose hexagonal; ADR-0001 stayed `proposed` until the answer, then `accepted` |
| Harness Engineer | Harness Engineer | blocked on 7 questions; the human answered the 3 costly ones (blocks incl. PIT download, ArchUnit, sensitive zones), the Orchestrator the 4 cheap ones |

Frictions: no `mvn` on the PATH (the Maven distribution was found under `~/.m2/wrapper`); PIT and ArchUnit were not all offline (PIT was downloaded with the human's approval, ArchUnit was already in `~/.m2`); the harness checks are Python scripts in a Java project (the skill's starters), which needs `python3` on the machine.

## Feature, edge cases

| Request | Stories | Reviews | NO-GO | Mutation |
|---|---|---|---|---|
| Book a slot | 2 | 2 | 0 | 100% (18 mutants) |
| Edge: blank identifiers | 1 | 1 | 0 | 100% (29) |
| Edge: simultaneous bookings | 1 | 1 | 0 | 100% (29, lock outside the scope) |

- Questions that reached the human: about 20 (Product Manager bets and PRD rules, architecture, harness, two story-2 business rules, three edge-case rules). Decision log: 37 entries, roughly half read by a person, the rest `answered-by-delegate` (Orchestrator's relay of a recommendation, nobody read it).
- This time the Product Owner escalated technical questions as its role file says; I answered them as delegate and the log shows the supersession (D-23 and D-24 `human-needed`, then D-25 and D-26). In the first example I had forced it to answer them. Same role, two behaviors, depending on what I asked it.
- The Architect did not write an ADR for the lock ("single process") in the simultaneous request, where in the first example the Architect wrote ADR-0002 for the equivalent queue. Both reasoned from their role file; the choice differs. Left as is.

Where a role avoided an error (evidence):
- The Planner of story 2 found that the PRD's overlap formula (`start < otherEnd && otherStart < end`) and its sentence ("share more than zero time") disagree for a zero-length slot, and asked what a valid range is (D-27) instead of choosing.
- The Developer of the simultaneous request showed with a manual lock-removal that its first test gate let a test pass without the lock (1 run in 10), found the cause (a thread blocked for another reason counted as held back) and fixed the gate before handing over. The Reviewer reproduced the lock-removal in a scratch copy and found a second mutant ("save outside the lock") caught only by luck.
- The Reviewer of story 1 rated `NoSuchElementException` on an unknown slot a `major`, though the Developer had listed it; the next story closed it.

Where a role did not avoid an error:
- The Product Manager stated two boundary conventions without source (back-to-back slots do not overlap; a slot starting exactly now can be booked) and flagged them as non-blocking. Nobody read them, so they sit in the log as delegated decisions (D-19, D-20).
- Story 1 shipped, then merged-in-spirit, with a `null` patient accepted and stored, which made every later booking throw `NullPointerException` (found by the Reviewer of story 2 as a minor; closed by the blank-identifiers request). Identifiers had been deferred on purpose (D-22).
- The 500 ms wait in the concurrency tests of story 2 could let them pass without the lock on a slow machine. The Reviewer of story 2 flagged it as a minor; the simultaneous request replaced it.

## Flag for the human

If B and C race for slot S and C already holds slot X which overlaps S, C sees `TAKEN` or `OVERLAPPING` depending on arrival order. Both are outcomes of a sequential order (D-21, D-35), so no document is broken. Making it `TAKEN` in every order would be a new product rule. The Planner flagged it, the Reviewer ruled it not a `major`; nobody asked you.

## Totals and limits

- Runs: 2 stories, 2 edge-case requests. Reviews: 4 of the diff. NO-GO: 0. Failure Analyst: never ran. The Developer and Reviewer loop never went round.
- No regression planted in this example (only the first has one).
- Sensitive zones: the review of story 1 and story 2 returned `escalate` (the bookings storage adapter); no person reviewed the adapter. The later two requests touched no zone.
- Tests: 35 (no counting of the ArchUnit rules, which are excluded from the default run); business test-cases: 35, each with a source and an exact automated test; mutation 100% on `domain` and `application` only.
- Not verified: nothing was run in a client with the roles installed (each role was a fresh agent that read its role file); the mutation threshold is still unset (a human decision); `adapters` is outside the mutation scope.

## What the Orchestrator did itself

Wrote the idea, the briefs and the metrics; relayed every question; answered the cheap technical ones as delegate; asked the human the costly ones with `AskUserQuestion` (about 20 answers in total). No code, test, plan or review. Chose the order of the edge-case requests and asked the Product Manager for the two edge-case PRDs on the human's behalf.
