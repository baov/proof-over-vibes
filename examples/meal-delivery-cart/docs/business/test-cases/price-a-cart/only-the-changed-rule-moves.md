---
feature: price-a-cart
type: functional
priority: high
source: PRD R4, R6, D-2; Story 1 criterion 7
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::changing one rule parameter changes the result and nothing else
status: covered
---

# Changing one rule parameter changes the result and nothing else

- Given: the same cart priced with a delivery fee of 250, then of 400, then with rules in another currency
- When: each is priced
- Then: only the fee line and the total move with the fee; with another currency only the currency of the amounts changes; no amount, rate or currency is built in
