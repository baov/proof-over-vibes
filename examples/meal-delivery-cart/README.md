# Meal delivery cart: an example

A small Kotlin module (price a cart: dishes, a percentage promotion, a delivery fee, exact money with rounding) built from a one-sentence idea by the roles and skills of this repository. Nothing here was written by hand except the idea, the briefs and these notes.

> Idea: "A meal-delivery cart where customers add dishes, apply promotions and see the delivery fees before they order."

Only the pricing is built; adding dishes, order handoff, tax and tip stay in the backlog.

## What you get

| From | You get | Where |
|---|---|---|
| The idea | market watch (sourced or marked *unverified*), vision, roadmap, story map, backlog, a PRD for the picked feature, two edge-case PRDs | [`docs/product/`](docs/product) |
| The questions | 46 numbered decisions with their source, about half read by a person | [`docs/business/decisions.md`](docs/business/decisions.md) |
| The code | the module and its tests (JUnit + kotlin-test, ArchUnit rules) | [`src`](src) |
| The tests | 76 business test-cases, each naming its source and its automated test, checked by a bridge | [`docs/business/test-cases`](docs/business/test-cases/price-a-cart) |
| The architecture | four ADRs, three turned into executable invariants | [`docs/technical`](docs/technical) |
| The checks | a harness (layers, rounding in one place, no `Double`/`BigDecimal` for money, a pure core, final fields, test-case bridge, mutation with PIT) | [`tools/harness`](tools/harness) |
| Each change | its plan, its notes, its metrics | [`.plans/done/`](.plans/done), [`.metrics/`](.metrics) |

## What you would not have without the repository

- **Money rules traced to a decision.** Every amount a caller sees (what is rounded, when, in which direction, which refusal wins) cites a PRD line or one of 46 decisions; where nobody had decided, an agent asked.
- **Reviews that check numbers, not style.** The Reviewers compared rounding against an independent `BigInteger` reference over millions of cases, and redid the Developer's manual mutations of the exact arithmetic that PIT cannot see.
- **A flaw found by a review and not by the tests:** the rate scales the rules accepted could not price ordinary amounts.

## Where a role avoided an error, and where it did not

- Avoided: two contradictions between an ADR/architect note and a decision (Planner, twice); unusable rate scales (Reviewer); `Math.*Exact` calls unprotected by PIT (Developer).
- Not avoided: negative amounts gave a negative total in merged code until a later request; accepted scales that did not work; and the last requirement (a pricing never waits for another) has no check at all.

Evidence with the commits is in [`RUN-NOTES.md`](RUN-NOTES.md).

## What the example does not show

- **No bug and no regression:** only the first example has one.
- **No NO-GO:** every review was a GO at the first pass; the Developer and Reviewer loop and the Failure Analyst never ran.
- **No review of the money zone by a person:** every review escalated, nobody read the diffs.
- **No money in motion:** one currency per pricing, no tax, tip or order handoff; no UI, storage or network.
- **Roles not installed in a client:** each was started as a fresh agent that read its role file.
- **Mutation score is raw:** 82.3%, with a dozen equivalent mutants; no threshold is set.

## Run it

Maven is not on the PATH of the machine this was built on; use any Maven 3.9 with JDK 21.

```bash
mvn test
bash tools/harness/run_all.sh --with-mutation   # needs python3, and PIT and ArchUnit in ~/.m2
```
