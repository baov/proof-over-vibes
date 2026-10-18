---
feature: price-a-cart
type: functional
priority: medium
source: PRD C2, C3, D-41
automated_test: src/test/kotlin/io/example/mealcart/application/ConcurrentPricingTest.kt::simultaneous pricings of one cart give the result each gives alone
status: covered
---

# Simultaneous pricings give the result each gives alone

- Given: one cart and one set of rules priced at the same moment many times, with a valid code, an unknown code, a valid code below the minimum, a blank code and no code
- When: all the pricings run together
- Then: each result equals the result the same call gives alone; the cart and the rules are unchanged
