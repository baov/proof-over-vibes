---
feature: price-a-cart
type: functional
priority: medium
source: PRD R11; Story 2 criterion 12
automated_test: src/test/kotlin/io/example/mealcart/application/ApplyPromotionTest.kt::without a code the discount is zero even when the rules hold a promotion
status: covered
---

# Without a code the discount is zero even when the rules hold a promotion

- Given: rules that hold a promotion and a cart priced with no code
- When: the cart is priced
- Then: the discount is zero, no reason is given and the total is the subtotal plus the fee
