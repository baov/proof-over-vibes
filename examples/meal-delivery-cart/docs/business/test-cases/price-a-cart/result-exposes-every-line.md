---
feature: price-a-cart
type: functional
priority: high
source: PRD R2, D-31; Story 1 criteria 2, 13
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::the result exposes subtotal, discount, fee line and total
status: covered
---

# The result exposes every line of the breakdown

- Given: a cart of 350 x 2 and 1200 x 1 and a delivery fee of 250, in euros
- When: the cart is priced
- Then: the result has named fields in this order: subtotal 1900, discount 0, fee line 250, total 2150
