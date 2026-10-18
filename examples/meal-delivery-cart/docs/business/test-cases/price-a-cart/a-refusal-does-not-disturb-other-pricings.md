---
feature: price-a-cart
type: functional
priority: medium
source: PRD C4, C5
automated_test: src/test/kotlin/io/example/mealcart/application/ConcurrentPricingTest.kt::a refusal in one thread does not disturb the other pricings
status: covered
---

# A refusal does not disturb other pricings

- Given: pricings of a cart in another currency (refused) and of a good cart at the same moment
- When: they all run together
- Then: every refused pricing gets the same refusal and every good pricing gets its own result
