# Run notes

Idea (from the human): "Renting parking spaces within a co-ownership." Python 3.14, stdlib `unittest` (pytest and any download were unavailable). Built with the roles of this repository, each started as a fresh agent that read its role file, watched on the office floor (`tools/office`). The human answered the product questions in chat.

## What ran

| Phase | Roles | Outcome |
|---|---|---|
| Product | Product Manager | framing, research (all *unverified*), vision, roadmap, story map, backlog; PRD of F1.2 "Register lots and spaces", 9 requirements |
| Foundations | Architect, Harness Engineer | clean architecture, JSON file, application API with an explicit role (ADR-0001..0003); executable layers rule, shape checks, test-case bridge, a stdlib mutation script |
| Feature F1.2 | Product Owner, then per story Planner, Developer, Reviewer | S1 register and list, S2 correct owner and number, S3 remove a space |

Reviews: 4 (S1, S2 twice, S3), all GO, no NO-GO. Failure Analyst never ran. Every review escalated: the manager-only check and the JSON store are sensitive zones, and the human accepted each.

Final state: 72 tests, 28 business test-cases all bridged to a test, mutation 90.6% on the critical scope (5 equivalent survivors), threshold 90 set as `warn`. 23 decisions in `docs/business/decisions.md`, every one answered by a person.

## Where the loop did something

- S1's Reviewer found two majors no test covered: a corrupt store raised a raw error, and `p10` sorted before `p2`. Both were carried, then fixed in S2 by explicit decisions (D-19, D-20).
- S2's Reviewer found a new crash in the natural sort (`²` is `isdigit()` but not `\d`). The human asked for the fix before accepting: one Developer/Reviewer iteration, red test first, GO on the second review.

## Limits

- The S1 Developer wrote code before tests (said so in its note); S2 and S3 were asked to go red first and showed it. Nothing was committed during the run, so the Reviewer could only check that claim from the tests.
- Mutation is a home-made script: it cannot see removed statements, changed messages or exception types, nor crash-mid-write atomicity.
- The French legal rules (epic E5) were never supplied: the human chose to provide the list and has not. Rentals (E3) do not exist: the rental check of requirement 7 is a port that always answers "no rental".
- Open minors: more than 4300 digits in an identifier raises a raw error; `StoreUnreadable` is not a `Refusal`; an `OSError` on the store is not converted; two S3 test-cases name an in-memory test where the file-level test is a different one.
- No UI or CLI: the public entry point is a Python API.
