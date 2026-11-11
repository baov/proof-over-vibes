# Run notes

Idea (from the human): "Renting parking spaces within a co-ownership." Python 3.14, stdlib `unittest` (pytest and any download were unavailable). Built with the roles of this repository, each started as a fresh agent that read its role file, watched on the office floor (`tools/office`). The human answered the product questions in chat.

## What ran

| Phase | Roles | Outcome |
|---|---|---|
| Product | Product Manager | framing, research (all *unverified*), vision, roadmap, story map, backlog; PRD of F1.2 "Register lots and spaces", 9 requirements |
| Foundations | Architect, Harness Engineer | clean architecture, JSON file, application API with an explicit role (ADR-0001..0003); executable layers rule, shape checks, test-case bridge, a stdlib mutation script |
| Feature F1.2 | Product Owner, then per story Planner, Developer, Reviewer | S1 register and list, S2 correct owner and number, S3 remove a space |

Reviews: 9 (S1, S2 twice, S3, E5 S1, then F2.1 S1 to S4), all GO, no NO-GO. Failure Analyst never ran. Every review escalated: the manager-only check and the JSON store are sensitive zones, and the human accepted each.

Final state: 303 tests, 109 business test-cases all bridged to a test, mutation 91.3% on the critical scope (equivalent survivors only), threshold 90 set as `warn`. 71 decisions in `docs/business/decisions.md`, every one answered by a person.

## Where the loop did something

- S1's Reviewer found two majors no test covered: a corrupt store raised a raw error, and `p10` sorted before `p2`. Both were carried, then fixed in S2 by explicit decisions (D-19, D-20).
- S2's Reviewer found a new crash in the natural sort (`²` is `isdigit()` but not `\d`). The human asked for the fix before accepting: one Developer/Reviewer iteration, red test first, GO on the second review.

## Limits

- The S1 Developer wrote code before tests (said so in its note); S2 and S3 were asked to go red first and showed it. Nothing was committed during the run, so the Reviewer could only check that claim from the tests.
- Mutation is a home-made script: it cannot see removed statements, changed messages or exception types, nor crash-mid-write atomicity.
- The French legal rules (epic E5) were never supplied: the human chose to provide the list and has not. Rentals (E3) do not exist: the rental check of requirement 7 is a port that always answers "no rental".
- Open minors: more than 4300 digits in an identifier raises a raw error; `StoreUnreadable` is not a `Refusal`; an `OSError` on the store is not converted; two S3 test-cases name an in-memory test where the file-level test is a different one.
- No UI or CLI: the public entry point is a Python API.

## Frictions to feed back to the roles and skills

Noted during the F2.1 run (offer a space). None was fixed in the run; the example does not edit `agents/` or `skills/`.

- **Test volume has no brake.** F2.1 took the suite from 125 to about 300 tests for roughly 1 200 lines of source (tests about 2.3 times larger), 128 of them for three use cases. Nothing in the roles or skills mentions the volume of tests. Causes: the Planner's step 5 (called twice, with nothing, with an invalid value, at the edge, in another order) turns every public parameter into several cases; each decision becomes a test-case and the bridge wants an automated test for each; the mutation threshold rewards one more test per killed mutant. Some tests protect nothing real (a test that an old call without the new argument raises `TypeError`; one test per bad input type). Candidates: the Planner groups the variants of one case; the Developer writes one parameterized test per case; the Reviewer reports tests that kill no mutant and tests that restate another; `behavior-driven-testing` says when not to add a test.
- **`run_mutation.py --scope diff` does nothing in a nested example folder** (it joins the repository-relative paths of `git diff --name-only` onto the project root, so nothing matches and it exits 0). Confirmed by the Reviewer of S2; `--relative` on the git call fixes it. A gate that passes by doing nothing.
- **The Developer wrote test-cases as `covered` instead of `pending` first** in S1; the plan's Deviations section was left empty (review 06, m6).
