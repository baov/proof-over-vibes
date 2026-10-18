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
