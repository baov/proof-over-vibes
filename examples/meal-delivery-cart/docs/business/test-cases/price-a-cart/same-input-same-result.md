---
feature: price-a-cart
type: functional
priority: high
source: PRD R3, R5; Story 1 criterion 8
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::the same cart and rules give the same result, whatever the line order
status: covered
---

# The same cart and rules always give the same result

- Given: a cart and rules priced twice, and the same lines in a different order
- When: each is priced
- Then: the results are equal
