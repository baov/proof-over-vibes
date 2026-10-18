---
feature: price-a-cart
type: functional
priority: medium
source: PRD C5, D-41
automated_test: src/test/kotlin/io/example/mealcart/application/ConcurrentPricingTest.kt::different carts priced at once never mix
status: covered
---

# Different carts priced at once never mix

- Given: several carts that differ by one line, priced at the same moment with the same rules
- When: each cart is priced many times together with the others
- Then: each result is the result of its own cart, with the exact sum of its own lines
