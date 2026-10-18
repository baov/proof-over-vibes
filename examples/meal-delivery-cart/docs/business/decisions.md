# Decision log

Append only. `answered` = a person read and answered; `answered-by-delegate` = a role's recommendation relayed by the orchestrator, nobody read it.

### D-1 Positioning: a fee-transparent cart for customers
- status: answered
- answer: Positioning: a fee-transparent cart for customers
- source: human; docs/product/research.md
- request: product-phase

### D-2 Market-agnostic: money rules and amounts are parameters
- status: answered
- answer: Market-agnostic: money rules and amounts are parameters
- source: human; docs/product/vision.md
- request: product-phase

### D-3 No real carts provided: the question of existing carts stays unverified
- status: answered
- answer: No real carts provided: the question of existing carts stays unverified
- source: human; docs/product/research.md
- request: product-phase

### D-4 The three success measures O1 to O3
- status: answered
- answer: The three success measures O1 to O3
- source: human; docs/product/vision.md
- request: product-phase

### D-5 First slice = dishes, one fee, one promotion type, live total, all rules as parameters; horizons Now/Next/Later
- status: answered
- answer: First slice = dishes, one fee, one promotion type, live total, all rules as parameters; horizons Now/Next/Later
- source: human; docs/product/roadmap.md
- request: product-phase

### D-6 Prioritization: MoSCoW, then value/effort
- status: answered
- answer: Prioritization: MoSCoW, then value/effort
- source: human; docs/product/backlog.md
- request: product-phase

### D-7 Picked backlog items 4 to 7 as the feature "price a cart"
- status: answered
- answer: Picked backlog items 4 to 7 as the feature "price a cart"
- source: human; docs/product/backlog.md
- request: product-phase

### D-8 Promotion = percentage off the food subtotal
- status: answered
- answer: Promotion = percentage off the food subtotal
- source: human; docs/product/prd/price-a-cart.md R7
- request: price-a-cart

### D-9 An inapplicable code or a subtotal below the minimum parameter gives a cart priced without discount, reason stated in the result; the discount never exceeds the subtotal
- status: answered
- answer: An inapplicable code or a subtotal below the minimum parameter gives a cart priced without discount, reason stated in the result; the discount never exceeds the subtotal
- source: human; docs/product/prd/price-a-cart.md R9, R10
- request: price-a-cart

### D-10 One flat delivery fee, a parameter, independent of the promotion; the promotion discounts food only
- status: answered
- answer: One flat delivery fee, a parameter, independent of the promotion; the promotion discounts food only
- source: human; docs/product/prd/price-a-cart.md R12, R13
- request: price-a-cart

### D-11 Each computed amount rounded once, half up, to the currency's smallest unit; total = sum of rounded lines
- status: answered
- answer: Each computed amount rounded once, half up, to the currency's smallest unit; total = sum of rounded lines
- source: human; docs/product/prd/price-a-cart.md R14, R16
- request: price-a-cart

### D-12 Architectural style: hexagonal light
- status: answered
- answer: Architectural style: hexagonal light
- source: human; docs/technical/adr/0001-hexagonal-light-architecture.md
- request: price-a-cart

### D-13 Money type Money(minorUnits: Long, currency) with an exact decimal percentage
- status: answered
- answer: Money type Money(minorUnits: Long, currency) with an exact decimal percentage
- source: human; docs/technical/adr/0002-money-as-minor-units-long.md
- request: price-a-cart

### D-14 Harness blocks A + B + D
- status: answered
- answer: Harness blocks A + B + D
- source: human; docs/technical/invariants.md
- request: price-a-cart

### D-15 Sensitive zone: money computation and rounding
- status: answered
- answer: Sensitive zone: money computation and rounding
- source: human; docs/technical/invariants.md
- request: price-a-cart

### D-16 Empty cart gives zero subtotal, discount and total and no fee; a line with quantity zero is refused as invalid input (flagged by the Product Manager as a bet a person should confirm)
- status: answered-by-delegate
- answer: Empty cart gives zero subtotal, discount and total and no fee; a line with quantity zero is refused as invalid input (flagged by the Product Manager as a bet a person should confirm)
- source: product-manager recommendation relayed by the orchestrator; docs/product/prd/price-a-cart.md R17, R18
- request: price-a-cart

### D-17 The four architecture invariants enforced via ArchUnit
- status: answered-by-delegate
- answer: The four architecture invariants enforced via ArchUnit
- source: harness-engineer recommendation relayed by the orchestrator; docs/technical/invariants.md
- request: price-a-cart

### D-18 Invariants start in warn mode
- status: answered-by-delegate
- answer: Invariants start in warn mode
- source: harness-engineer recommendation relayed by the orchestrator; docs/technical/invariants.md
- request: price-a-cart

### D-19 Shape thresholds skipped (no detekt download)
- status: answered-by-delegate
- answer: Shape thresholds skipped (no detekt download)
- source: harness-engineer recommendation relayed by the orchestrator; docs/technical/invariants.md
- request: price-a-cart

### D-20 Mutation scope: domain and application, no threshold
- status: answered-by-delegate
- answer: Mutation scope: domain and application, no threshold
- source: harness-engineer recommendation relayed by the orchestrator; docs/technical/invariants.md
- request: price-a-cart

### D-21 AGENTS.md Harness section; no pre-commit or CI file
- status: answered-by-delegate
- answer: AGENTS.md Harness section; no pre-commit or CI file
- source: harness-engineer recommendation relayed by the orchestrator; docs/technical/invariants.md
- request: price-a-cart

### D-22 Rate parameter must be between 0 and 100 percent, otherwise the rules are rejected
- status: answered
- answer: Rate parameter must be between 0 and 100 percent, otherwise the rules are rejected
- source: human; stories.md open point 1 (option A)
- request: price-a-cart

### D-23 Unknown code and subtotal below minimum together: the unknown-code reason is given, one reason only
- status: answered
- answer: Unknown code and subtotal below minimum together: the unknown-code reason is given, one reason only
- source: human; stories.md open point 3 (option A)
- request: price-a-cart

### D-24 D-16 confirmed: empty cart gives zero subtotal, discount and total and no fee; a line with quantity zero is refused as invalid input
- status: answered
- answer: D-16 confirmed: empty cart gives zero subtotal, discount and total and no fee; a line with quantity zero is refused as invalid input
- source: human; stories.md open point 6; PRD R17, R18
- supersedes: D-16
- request: price-a-cart

### D-25 Empty cart with a code is a subtotal of zero, below any positive minimum, with the same reasons as R9
- status: answered-by-delegate
- answer: Empty cart with a code is a subtotal of zero, below any positive minimum, with the same reasons as R9
- source: orchestrator, simplest option; stories.md open point 2 (option A)
- request: price-a-cart

### D-26 The fee parameter is already in minor units, so R14 never changes it
- status: answered-by-delegate
- answer: The fee parameter is already in minor units, so R14 never changes it
- source: orchestrator, simplest option; stories.md open point 4 (option A)
- request: price-a-cart

### D-27 A line holds a unit price only; a line currency is impossible by construction
- status: answered-by-delegate
- answer: A line holds a unit price only; a line currency is impossible by construction
- source: orchestrator, simplest option; stories.md open point 5 (option B)
- request: price-a-cart

### D-28 An out-of-range rate is rejected by an exception raised when the rules are built, so no cart is priced with them
- status: answered-by-delegate
- answer: exception raised at rules construction
- source: orchestrator, cheap to reverse; D-22; .plans/in-progress/price-a-cart/architect.md
- request: price-a-cart

### D-29 The bounds 0 and 100 percent are both valid (inclusive)
- status: answered-by-delegate
- answer: inclusive
- source: orchestrator, cheap to reverse; D-22
- request: price-a-cart


### D-30 Negative or overflowing amounts: stay reserved (no rule, no test; natural behavior undocumented)
- status: answered-by-delegate
- answer: (a) leave reserved
- source: orchestrator relaying plan.md section 6 Q1; PRD section 6
- request: price-a-cart

### D-31 Shape of the result: named fields in R2 order (subtotal, discount, feeLine, total); feeLine absent for the empty cart
- status: answered-by-delegate
- answer: (a) named fields
- source: orchestrator relaying plan.md section 6 Q2; PRD R2, R17; D-24
- request: price-a-cart

### D-32 A non-empty cart with a zero subtotal (every unit price 0) is accepted and still has the fee line
- status: answered-by-delegate
- answer: (a) accepted, fee line applies
- source: orchestrator relaying plan.md section 6 Q3; PRD R12, R17, R18
- request: price-a-cart

### D-33 Promotion reasons: closed set UNKNOWN_CODE and SUBTOTAL_BELOW_MINIMUM in one field; empty when the promotion applied or no code was supplied; a valid code whose discount rounds to zero is applied (discount zero, no reason)
- status: answered
- answer: (a) closed set of two reasons in one field
- source: human; apply-a-promotion plan.md Q1; PRD R9
- request: price-a-cart

### D-34 The promotion is optional in the rules (rules without one are valid, any supplied code is then unknown); one promotion = one code, one rate, one minimum; the code matches by exact text (case-sensitive, no trimming)
- status: answered
- answer: (a) optional promotion, exact-text match
- source: human; apply-a-promotion plan.md Q2; PRD R7, R9
- request: price-a-cart

### D-35 Percentage(numerator, scale) is numerator over 10^scale as a fraction of the amount, scale 0..18; a negative numerator is built but refused by the rules per D-28
- status: answered-by-delegate
- answer: (a) as stated
- source: orchestrator relaying apply-a-promotion plan.md Q3; D-13, D-28
- request: price-a-cart

### D-36 Rate bounds are enforced by the rules, not by Percentage: Percentage validates only its scale; the rules reject any rate outside 0..100 percent (D-28 prevails over the architect note)
- status: answered-by-delegate
- answer: follow D-28 and the stories
- source: orchestrator; D-28, D-29; architect.md
- request: price-a-cart

### D-37 Negative quantity or negative unit price is refused as invalid input like quantity zero; a negative fee or minimum refuses the rules when built; a total is never negative
- status: answered
- answer: Negative quantity or negative unit price is refused as invalid input like quantity zero; a negative fee or minimum refuses the rules when built; a total is never negative
- source: human; docs/product/prd/price-a-cart-edge-amounts.md A7-A9
- supersedes: D-30 (for these points)
- request: price-a-cart-edge-amounts

### D-38 An amount beyond the money range gives no price and a refusal named 'amount too large', distinct from the other refusals, for every amount along the way
- status: answered
- answer: An amount beyond the money range gives no price and a refusal named 'amount too large', distinct from the other refusals, for every amount along the way
- source: human; docs/product/prd/price-a-cart-edge-amounts.md A2-A4, A10
- supersedes: D-30 (for these points)
- request: price-a-cart-edge-amounts

### D-39 Every accepted rate scale prices correctly; only a result beyond the range is refused as too large
- status: answered
- answer: Every accepted rate scale prices correctly; only a result beyond the range is refused as too large
- source: human; docs/product/prd/price-a-cart-edge-amounts.md A11-A12
- supersedes: D-30 (for these points)
- request: price-a-cart-edge-amounts

### D-40 A blank or empty code supplied with a cart means no code: no discount, no reason; a blank or empty promotion code in the rules is refused when the rules are built
- status: answered
- answer: A blank or empty code supplied with a cart means no code: no discount, no reason; a blank or empty promotion code in the rules is refused when the rules are built
- source: human; docs/product/prd/price-a-cart-edge-codes-and-concurrency.md C7-C8
- request: price-a-cart-edge-codes-and-concurrency

### D-41 Simultaneous pricings need no new rule: C2-C6 restate R3 and R5 (nobody read this)
- status: answered-by-delegate
- answer: Simultaneous pricings need no new rule: C2-C6 restate R3 and R5 (nobody read this)
- source: orchestrator; docs/product/prd/price-a-cart-edge-codes-and-concurrency.md C2-C6; PRD R3, R5
- request: price-a-cart-edge-codes-and-concurrency

### D-42 A line in another currency than the rules together with an amount too large: the currency refusal (IllegalArgumentException) always wins, whatever the amounts
- status: answered-by-delegate
- answer: option A
- source: orchestrator relaying edge-amounts plan.md Q1; docs/product/prd/price-a-cart-edge-amounts.md; docs/technical/adr/0003-*
- request: price-a-cart-edge-amounts

### D-43 What the caller learns from 'amount too large' is the type alone (AmountTooLargeException in domain.money, an ArithmeticException); the message is for humans, not a contract, and does not name which amount
- status: answered-by-delegate
- answer: option A
- source: orchestrator relaying edge-amounts plan.md Q2; docs/product/prd/price-a-cart-edge-amounts.md; docs/technical/adr/0003-*
- request: price-a-cart-edge-amounts

### D-44 The public Money.times(rate) with a negative amount or a negative rate numerator is refused with IllegalArgumentException; zero is accepted
- status: answered-by-delegate
- answer: option A
- source: orchestrator relaying edge-amounts plan.md Q3; docs/product/prd/price-a-cart-edge-amounts.md; docs/technical/adr/0003-*
- request: price-a-cart-edge-amounts

### D-45 A code is 'blank' per Kotlin's isBlank: empty or only spaces, tabs, line breaks, no-break spaces (U+00A0, U+2007, U+202F), U+3000 and other Unicode space separators; U+001C..U+001F count as blank; U+0085, U+200B and U+FEFF do not; a code of invisible characters is an ordinary code (unknown on the cart side, accepted as a promotion code in the rules); same definition for the cart code and the rules' promotion code
- status: answered-by-delegate
- answer: option A (Kotlin's isBlank)
- source: orchestrator relaying edge-codes-and-concurrency plan.md Q1; PRD C7-C8; architect note; D-40
- request: price-a-cart-edge-codes-and-concurrency

### D-46 Amendment: a blank code amends D-33 and D-34 for blank codes only (a blank cart code means no code, no reason; a blank promotion code in the rules is refused when built); D-40 already supersedes them for those points
- status: answered-by-delegate
- answer: amendment noted
- source: orchestrator relaying the Planner's note; D-33, D-34, D-40
- request: price-a-cart-edge-codes-and-concurrency
