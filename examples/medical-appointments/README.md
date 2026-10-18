# Medical appointments: an example

A small Java 21 module (a patient books a practitioner's free slot; taken, past, unknown, overlapping or blank requests are refused; simultaneous bookings are safe), built from a one-sentence idea by the roles and skills of this repository. Nothing here was written by hand except the idea, the briefs and these notes.

> Idea: "An online booking service for medical appointments where patients see a practitioner's free slots, book one, and cancel it."

Only the first verb (book) is built; cancelling and availability stay in the backlog.

## What you get

| From | You get | Where |
|---|---|---|
| The idea | market watch (sourced or marked *unverified*), vision, roadmap, story map, backlog, a PRD for the picked feature, two edge-case PRDs | [`docs/product/`](docs/product) |
| The questions | 37 numbered decisions with their source, about half read by a person | [`docs/business/decisions.md`](docs/business/decisions.md) |
| The code | the module, JUnit tests and ArchUnit rules | [`src`](src) |
| The tests | 35 business test-cases, each naming its source and its automated test, checked by a bridge | [`docs/business/test-cases`](docs/business/test-cases/book-a-slot) |
| The architecture | one ADR (hexagonal), turned into executable invariants | [`docs/technical`](docs/technical) |
| The checks | a harness (layers, test-case bridge, mutation with PIT) | [`tools/harness`](tools/harness) |
| Each change | its plan, its notes, its metrics | [`.plans/done/`](.plans/done), [`.metrics/`](.metrics) |

## What you would not have without the repository

- **A person called where it matters.** About 20 questions reached the human (positioning, country, the shape of the first slice, the architectural style, a PIT download, what a valid slot is, what the loser of a race sees). Cheap technical ones were answered by the Orchestrator and logged as delegated.
- **Rules nobody invented.** The overlap rule in the PRD contradicted itself for a zero-length slot; the Planner caught it and asked rather than picking one reading.
- **A concurrency claim that is tested, not asserted.** Removing the lock turns 7 of 9 tests red on every run; the first version of the test gate let a test pass in 1 run out of 10, and the Developer found and fixed that before handing over.

## Where a role avoided an error, and where it did not

- Avoided: the PRD's overlap inconsistency (Planner); a weak test gate (Developer); an unknown-slot exception that no document had settled (Reviewer).
- Not avoided: two boundary conventions written by the Product Manager with no source and read by nobody; a `null` patient stored by story 1 until a later request refused it.

Evidence with commits is in [`RUN-NOTES.md`](RUN-NOTES.md).

## What the example does not show

- **No bug and no regression:** only the first example has one.
- **No NO-GO:** every review was a GO at the first pass; the Developer and Reviewer loop and the Failure Analyst never ran.
- **Part of the sensitive-zone review is missing:** the bookings storage adapter was flagged twice and nobody reviewed it.
- **In memory only:** no database, network, UI or accounts; the lock is valid in one process.
- **Roles not installed in a client:** each was started as a fresh agent that read its role file.

## Run it

Maven is not on the PATH of the machine this was built on; use any Maven 3.9 with JDK 21.

```bash
mvn test
bash tools/harness/run_all.sh --with-mutation   # needs python3 and PIT in ~/.m2
```
