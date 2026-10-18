---
feature: price-a-cart
type: functional
priority: medium
source: PRD C3, C7
automated_test: src/test/kotlin/io/example/mealcart/application/ConcurrentPricingTest.kt::an empty cart priced at once with a blank code or no code gives the same result
status: covered
---

# An empty cart priced at once

- Given: an empty cart priced at the same moment with a blank code and with no code
- When: the pricings run together
- Then: every result is the same
