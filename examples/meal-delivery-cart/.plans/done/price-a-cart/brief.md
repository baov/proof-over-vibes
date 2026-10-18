# Brief: price a cart

- Request type: prompt (cites the PRD)
- Slug: price-a-cart
- Iteration counter: 0 (for the feature; each story has its own counter in its subfolder)
- Iteration limit: 5
- Delegation: middle way. The Orchestrator answers cheap-to-reverse technical questions with the role's recommendation (`answered-by-delegate`); product bets and costly-to-reverse choices go to the human (`answered`).

## Objective

Implement the feature described by the PRD `docs/product/prd/price-a-cart.md` (status ready): price a cart from lines (unit price, quantity), a percentage promotion, one flat delivery fee and a currency, all rules supplied as parameters. Pure domain behavior: no UI, no payment, no order handoff, no catalogue.

## Acceptance criteria

The 18 requirements of the PRD, section 5. Its reserved open questions (negative or overflowing amounts, blank or empty identifiers and codes, two operations on one cart at the same moment) are NOT decided: a role that meets one asks. The PRD's empty-cart and quantity-zero requirements (R17, R18) were delegated, not read by a person.

## Fixed by the human (stack, given in the request)

Kotlin 2.2.0 on JDK 21, Maven (the Maven distribution under `~/.m2/wrapper/dists`, no `mvn` on the PATH), `kotlin-test` and JUnit Jupiter 5.12.2 (checked offline: `kotlin-test-junit5` is NOT usable offline). Only artifacts already in `~/.m2/repository` can be used without a download; any other dependency or plugin is a question for the human. PIT (mutation) is already in `~/.m2` from another example. Everything else (structure, style) is for `architect` to propose.

## Carried over

None (first request of the project).

## Answers

(none yet)
