---
feature: price-a-cart
type: functional
priority: high
source: PRD A9, D-37
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::no amount of a price is negative
status: covered
---

# No amount of a price is negative

- Given: carts of zero price, odd and even subtotals, with rates of 100 percent and 99.9 percent and a fee
- When: the cart is priced with the code
- Then: subtotal, discount, fee line and total are never negative, the discount never exceeds the subtotal, and the total is subtotal minus discount plus fee
