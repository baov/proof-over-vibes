---
feature: price-a-cart
type: functional
priority: high
source: PRD R17, D-24; Story 1 criterion 9
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::an empty cart gives zero amounts and no fee line
status: covered
---

# An empty cart has zero amounts and no fee line

- Given: a cart with no lines and a positive delivery fee
- When: the cart is priced
- Then: subtotal, discount and total are zero in the currency of the rules and the fee line is absent
