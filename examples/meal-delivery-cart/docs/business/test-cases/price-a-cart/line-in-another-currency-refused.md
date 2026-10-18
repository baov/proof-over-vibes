---
feature: price-a-cart
type: functional
priority: high
source: PRD R15, D-27; Story 1 criterion 11
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::a line priced in another currency than the rules is refused
status: covered
---

# A line in another currency than the rules is refused

- Given: rules in euros and a cart with a line whose unit price is in yen
- When: the cart is priced
- Then: pricing fails with an invalid-input error (IllegalArgumentException); no price is returned
