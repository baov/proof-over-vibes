---
feature: price-a-cart
type: functional
priority: high
source: PRD R9, D-9; Story 2 criterion 5
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::a subtotal below the minimum gives no discount and says why
status: covered
---

# A subtotal below the minimum gives no discount and says why

- Given: a valid code and a subtotal of 999 against a minimum of 1000
- When: the cart is priced with the code
- Then: the discount is zero, the reason is subtotal below minimum, the fee line is kept and the total is the subtotal plus the fee
