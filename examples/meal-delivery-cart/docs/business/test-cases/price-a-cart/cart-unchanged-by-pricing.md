---
feature: price-a-cart
type: functional
priority: high
source: PRD R5; Story 1 criterion 8
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::pricing leaves the cart unchanged
status: covered
---

# Pricing leaves the cart unchanged

- Given: a cart built from a list the caller then adds a line to
- When: the cart is priced
- Then: the cart still holds its original lines and the price does not change
