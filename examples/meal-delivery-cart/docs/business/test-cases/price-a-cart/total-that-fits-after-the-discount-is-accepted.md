---
feature: price-a-cart
type: functional
priority: high
source: PRD A10, A12, D-38
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::a total that fits after the discount is accepted although subtotal plus fee does not
status: covered
---

# A total that fits after the discount is accepted although subtotal plus fee does not

- Given: a subtotal at the largest amount with a discount of the whole subtotal and a fee; and a subtotal whose discounted amount plus the fee reaches the largest amount, or one unit beyond
- When: the cart is priced with the code
- Then: a total that fits is priced, however large an intermediate sum would be; the fee that pushes the total one unit beyond is refused as amount too large
