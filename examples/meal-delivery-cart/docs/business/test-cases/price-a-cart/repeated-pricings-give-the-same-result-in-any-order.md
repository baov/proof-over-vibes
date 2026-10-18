---
feature: price-a-cart
type: functional
priority: medium
source: PRD C6
automated_test: src/test/kotlin/io/example/mealcart/application/ConcurrentPricingTest.kt::repeated pricings give the same result in any order
status: covered
---

# Repeated pricings give the same result in any order

- Given: two carts priced one after the other many times, in one order and then in the other
- When: the pricings are repeated
- Then: each cart always gives the same result: nothing is remembered from an earlier pricing
