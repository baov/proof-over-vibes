---
feature: price-a-cart
type: functional
priority: medium
source: PRD C4
automated_test: src/test/kotlin/io/example/mealcart/application/ConcurrentPricingTest.kt::a pricing never fails or waits because of another
status: covered
---

# A pricing never fails because of another

- Given: many pricings of the same and of different carts at the same moment
- When: they all run together
- Then: every one finishes within the time limit and none fails
