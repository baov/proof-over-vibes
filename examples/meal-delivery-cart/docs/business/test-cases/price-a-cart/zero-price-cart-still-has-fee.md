---
feature: price-a-cart
type: functional
priority: high
source: PRD R12, R17, D-32; Story 1 criterion 14
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::a cart of free lines still has the fee line
status: covered
---

# A cart of free lines still has the fee line

- Given: a non-empty cart whose lines all have a unit price of 0, and a delivery fee of 250
- When: the cart is priced
- Then: subtotal and discount are zero, the fee line is present and equals 250, the total is 250
