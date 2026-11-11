# Co-ownership parking: an example

A small Python module (register the lots and parking spaces of a co-ownership, their owners, correct and remove them, list them) built from a one-sentence idea by the roles and skills of this repository, and watched live on the office floor (`tools/office`). Nothing here was written by hand except the idea, the briefs and these notes.

> Idea: "Renting parking spaces within a co-ownership."

> Built with the roles and skills of this repository as of the commit titled "Add TL;DR and diagrams to generated docs; durations, document reader and resting agents on the floor". The security and performance targets (PRD, Architect, review), added to `main` since, are not part of it.

Only the first feature of the backlog is built, the register (F1.2). The rentals, the French legal rules and the multi-co-ownership are in the backlog, not in the code.

## What you get

| From | You get | Where |
|---|---|---|
| The idea | framing, market watch (every claim marked *unverified*), vision, roadmap, story map, backlog, the PRD of the picked feature | [`docs/product/`](docs/product) |
| The questions | 23 numbered decisions with their source, every one answered by a person | [`docs/business/decisions.md`](docs/business/decisions.md) |
| The code | the module and its tests (stdlib `unittest`) | [`src`](src), [`tests`](tests) |
| The tests | 28 business test-cases, each naming its source and its automated test, checked by a bridge | [`docs/business/test-cases`](docs/business/test-cases) |
| The architecture | three ADRs (clean architecture, a JSON file, an application API with an explicit role), the first made executable | [`docs/technical`](docs/technical) |
| The checks | a harness: layers rule, shape limits, test-case bridge, and a stdlib mutation script (90.6% on the critical scope) | [`tools/harness`](tools/harness) |
| Each review | the Reviewer's report: verdict, findings with their severity, the probes behind them | [`reviews/`](reviews) |

## Where the loop did something

- A review found two defects no test covered (a corrupt store file raised a raw error; `p10` sorted before `p2`). They became decisions, then code.
- A second review found a new crash in the natural sort (`²`). The human asked for the fix before accepting: the example's only Developer and Reviewer iteration, red test first, GO on the second review.

## What the example does not show

- **No NO-GO, no Failure Analyst.**
- **No review of the sensitive zones by a person:** every review escalated, the human accepted each in chat, nobody read the diffs.
- **No security or performance target:** the roles predate them.
- **No rentals, no legal rules, no UI:** the rental check is a port that always answers "no rental"; the French rules were never supplied.
- **Roles not installed in a client:** each was started as a fresh agent that read its role file.
- **Mutation is a home-made script:** it cannot see removed statements, changed messages or exception types, nor crash-mid-write atomicity; five equivalent survivors remain.
- **`unittest`, not pytest:** nothing could be installed on the machine.

Evidence and the open minor findings are in [`RUN-NOTES.md`](RUN-NOTES.md).

## Run it

Python 3.14, nothing to install.

```bash
python3 -m unittest discover -s tests
bash tools/harness/run_all.sh
python3 tools/harness/run_mutation.py --scope critical
```
