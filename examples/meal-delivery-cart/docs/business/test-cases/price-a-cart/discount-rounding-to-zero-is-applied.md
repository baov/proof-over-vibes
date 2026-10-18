---
feature: price-a-cart
type: functional
priority: medium
source: PRD R8, R14, D-33; Story 2 criterion 12
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::a discount that rounds to zero is applied with no reason
status: covered
---

# A discount that rounds to zero is applied with no reason

- Given: a valid code at 1 percent and a subtotal of 10 (a discount of 0.1)
- When: the cart is priced with the code
- Then: the discount is zero, no reason is given and the total is the subtotal plus the fee
