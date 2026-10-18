---
feature: price-a-cart
type: functional
priority: medium
source: PRD R1; Story 1 criterion 1 (derived)
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::the same line twice in a cart counts twice
status: covered
---

# The same line twice counts twice

- Given: a cart with two equal lines of 350 x 2
- When: the cart is priced
- Then: the subtotal is 1400: lines have no identity and nothing merges them
