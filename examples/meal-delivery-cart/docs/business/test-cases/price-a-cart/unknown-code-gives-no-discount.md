---
feature: price-a-cart
type: functional
priority: high
source: PRD R9, D-9; Story 2 criterion 4, 13
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::an unknown code gives no discount and says why
status: covered
---

# An unknown code gives no discount and says why

- Given: rules with the promotion code WELCOME10, or rules with no promotion at all
- When: the cart is priced with another code
- Then: the discount is zero, the reason is the unknown code, the fee line is kept and the total is the subtotal plus the fee; pricing succeeds
