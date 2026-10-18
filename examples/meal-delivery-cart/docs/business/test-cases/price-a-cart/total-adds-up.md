---
feature: price-a-cart
type: functional
priority: high
source: PRD R13, R16; Story 1 criterion 5
automated_test: src/test/kotlin/io/example/mealcart/application/PriceCartTest.kt::the total is subtotal minus discount plus the fee line
status: covered
---

# The total adds up the lines shown

- Given: a subtotal of 1900 and a delivery fee of 250
- When: the cart is priced
- Then: the total is 2150 and equals subtotal minus discount plus fee line; with a fee of 0 the total equals the subtotal
