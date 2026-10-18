---
feature: price-a-cart
type: functional
priority: high
source: PRD R1, R14; Story 1 criterion 1
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::the subtotal is the sum of unit price times quantity
status: covered
---

# The subtotal is the exact sum of the lines

- Given: a cart with a line of 350 x 2 and a line of 1200 x 1, in euros
- When: the cart is priced
- Then: the subtotal is 1900, in the smallest unit; a single line of quantity one gives its unit price
