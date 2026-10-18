# Run notes

Written by the Orchestrator while the run happens. Honest log: what the roles did, what the human decided, and what the Orchestrator did itself.

## Delegation

Same middle way as the medical example: the Orchestrator answers cheap-to-reverse technical questions with the role's recommendation (`answered-by-delegate`); every bet of the Product Manager and every escalation of a role goes to the human (`answered`).

## Product phase

| Step | Role | Outcome |
|---|---|---|
| Idea (one sentence, written by the Orchestrator) | | "A meal-delivery cart where customers add dishes, apply promotions and see the delivery fees before they order." |
| Market watch | Product Manager | `research.md`; escalated 3 bets |
| Positioning, market, sources | human | fee-transparent cart for customers; market-agnostic (money rules are parameters); no real carts to check, stays *unverified* |
| Vision, story map | Product Manager | written; escalated success measures, first slice and horizons, prioritization |
| Success, slice, horizons, prioritization | human | the three measures; dishes + one fee + one promotion + live total; MoSCoW then value/effort |
| Roadmap, backlog | Product Manager | written, nothing picked |
| Backlog pick | human | items 4 to 7, "price a cart" |
| PRD | Product Manager | escalated 5 groups of money rules |
| Rules | human (Q1 to Q4), Orchestrator as delegate (Q5) | percentage promotion; no discount with a reason when it does not apply; flat delivery fee; round each amount once, half up. Q5 (empty cart, quantity zero) delegated, flagged by the PM as a bet that a person should confirm |
| PRD | Product Manager | ready; 18 requirements |

Environment: Kotlin 2.2.0 works fully offline with `kotlin-test` and JUnit Jupiter 5.12.2. `kotlin-test-junit5` does not: version 2.2.0 is not in `~/.m2`, and 1.9.25 pulls a JUnit 5.6.3 that is not either. Checked with a throwaway project before the run; nothing was downloaded.

## Foundations (empty project)

| Step | Role | Outcome |
|---|---|---|
| Request | Orchestrator | brief for "price a cart", citing the PRD; stack (Kotlin on JDK 21, Maven, kotlin-test, JUnit) given as the human's constraint |
| Architect | Architect | escalated two costly choices: the architectural style and the public money type. The human chose hexagonal (light) and `Money(minorUnits: Long, currency)`. ADR-0001 and ADR-0002 were written after the answers. The note's body kept reading as the old escalation note after the answer (only its front-matter was updated); the Architect cleaned it at the next pass |
| Harness Engineer | Harness Engineer | blocked on 7 questions; the human answered 2 (blocks incl. the test-case bridge; sensitive zone: money), the Orchestrator the 5 cheap ones |

## Features and edge cases

| Request | Stories | Reviews | NO-GO | Mutation (critical scope) |
|---|---|---|---|---|
| Price a cart | 2 | 2 | 0 | 91.7%, then 98.0% |
| Edge: amounts (negative, too large, rate scale) | 1 | 1 | 0 | 81.3% (12 equivalent mutants, see below) |
| Edge: blank codes and simultaneous pricing | 1 | 1 | 0 | 82.3% |

- Questions that reached the human: about 24 `AskUserQuestion` answers (positioning, market, success measures, first slice, prioritization, the pick, five money rules, architecture, money type, harness blocks, sensitive zone, three open points of story 1, two of story 2, four edge-case rules). The decision log has 46 entries: 24 `answered` (read by a person), 23 `answered-by-delegate` (nobody read), and a few that are `human-needed` or superseding.
- The Product Owner listed open points itself (rate range, empty cart with a code, which reason when two fail, line currency, fee precision). That is the role working as intended: its criteria all cite a document, the rest is a question.

Where a role avoided an error (evidence):
- The Planner of story 1 saw that the Architect's note (the fee goes through rounding) contradicted D-26 (the fee is already in minor units) and wrote down which one wins, without editing the Architect's note. The Planner of story 2 did the same for `Percentage` refusing negatives (Architect) against D-28 (the rules refuse them).
- The Reviewer of story 2 checked rounding against an independent `BigInteger` reference (62,986 random cases and 3.3 million small ones, no mismatch) and found that scales 10 to 18, accepted by D-35, could not price ordinary amounts (a Long overflow in subtotal x numerator). That became the "every scale prices correctly" rule of the amounts request.
- The Developer of the amounts request saw that PIT's default mutators do not touch `Math.*Exact`, and proved each exact call by a manual mutation, with the failing tests recorded. The Reviewer redid all six and added about 20 more.
- The Reviewer of the last request tried `@Synchronized` on the pricing function and a shared final array: the tests catch the array but nothing catches the lock.

Where a role did not avoid an error:
- The first version let negative quantity, unit price and fee through, giving a negative total. The Planner raised it as reserved, the Product Owner logged it as such (D-30), the Reviewer made it a `major`; it was fixed two requests later. Nothing broke, but a negative total existed in merged code before anyone decided.
- Scales 0 to 18 were accepted (a delegated decision, D-35) although most of them could not be used. Nobody checked until the review of story 2.
- The plan of the amounts request carried a wrong figure ("54 existing tests", there were 37) and was never brought up to date; the Developer and the Reviewer each noticed, nobody fixed the plan.
- Requirement C4 of the last request (a pricing never waits for another) has no check at all. The Reviewer called it a `major` and the run ended there: it is the one open point left.

Frictions and observations:
- The Product Manager marked the empty-cart rule (Q5) as a bet a person should confirm; it had been delegated. I asked the human at the next open question and logged it as confirmed (D-24).
- Kotlin: `kotlin-test-junit5` could not be used offline (2.2.0 is not in `~/.m2` and 1.9.25 pulls a missing JUnit 5.6.3). JUnit's own `@Test` with `kotlin.test` assertions worked and was written into every brief after a throwaway project proved it.
- PIT on Kotlin: 10 `Intrinsics.check*` null-check mutants and a dead inline body are equivalent mutants. They lowered the score from 98.0% to 81.3% without any lost protection. Without a threshold nothing fails on that; the Reviewer asked a person to record a baseline.
- PIT's default mutators skip `Math.*Exact`: the sums are protected by behavior tests only, which the Developer and the Reviewer checked by hand.
- The Planner wrote in a plan that "validating the plan counts as the human decision on the sensitive zone". It does not; the Orchestrator had the sentence removed. No person reviews plans or diffs here.

## Totals and limits

- Runs: 2 stories, 2 edge-case requests, no bug. Reviews: 4 of the diff. NO-GO: 0. Failure Analyst: never ran. No regression planted in this example.
- Sensitive zone (money): every review returned `escalate`; nobody reviewed the diffs.
- Tests: 78; business test-cases: 76, each with a source and an exact automated test; mutation 82.3% on `domain` and `application` (see above).
- Not verified: nothing ran in a client with the roles installed; the mutation threshold is unset; the last open major (C4) has no check; the comparison of `Percentage` (10, 2) against (100, 3) says two equal rates are different, carried and out of scope.

## What the Orchestrator did itself

Wrote the idea, the briefs and the metrics; relayed every question; answered the cheap technical ones as delegate and asked the human the others (about 24 answers); ran a throwaway Kotlin project to learn which test dependencies work offline. No code, test, plan or review.
